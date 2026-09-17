import json
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

from models.models import MessageResponse
from config import POSTGRES_USER, POSTGRES_PASSWORD

# base_dir = Path(__file__).resolve().parents[1]  # LLM
# db_dir = base_dir / ".databases"
# db_dir.mkdir(parents=True, exist_ok=True)
#
# db_path = db_dir / "context_memory.db"
DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/context_memory"


class ContextMemory:
    def __init__(
            self,
            llm,
            db_path: str = DB_URL,
            max_messages: int = 50,
    ):
        self.llm = llm
        self.engine = create_async_engine(db_path)
        self.max_messages = max_messages

    async def init(self):
        from sqlalchemy import Column, Integer, Text, MetaData, Table

        metadata = MetaData()
        message_table = Table(
            "message_store",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("session_id", Text),
            Column("message", Text),
        )

        async with self.engine.begin() as conn:
            await conn.run_sync(message_table.create, checkfirst=True)

    async def get_message_history(self, session_id: str) -> List[MessageResponse]:
        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT id, message
                    FROM message_store
                    WHERE session_id = :session_id
                    ORDER BY id ASC
                """),
                {"session_id": session_id},
            )

            rows = result.fetchall()

        messages: List[MessageResponse] = []

        for row in rows:
            raw = row.message

            # LangChain stores either dict or JSON string depending on version
            if isinstance(raw, str):
                data = json.loads(raw)
            else:
                data = raw

            msg_type = data.get("type")
            content = data.get("data", {}).get("content", "")

            if msg_type in ("human", "HumanMessage"):
                role = "user"
            elif msg_type in ("ai", "AIMessage", "AIMessageChunk"):
                role = "assistant"
            else:
                continue

            additional_kwargs = data.get("data", {}).get("additional_kwargs", {})
            timestamp = additional_kwargs.get("timestamp", datetime.now())

            messages.append(
                MessageResponse(
                    id=row.id,
                    role=role,
                    content=content,
                    timestamp=timestamp,
                )
            )

        messages.sort(key=lambda x: x.timestamp)
        return messages

    async def append_message(self, session_id: str, role: str, content: str):
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection=self.engine,
        )

        if role == "user":
            msg = HumanMessage(content=content)
        elif role == "assistant":
            msg = AIMessage(content=content)
        else:
            raise ValueError("Invalid role")

        await message_history.aadd_message(msg)

    async def delete_last_entry(self, session_id: str):
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    DELETE FROM message_store
                    WHERE id = (
                        SELECT id FROM message_store
                        WHERE session_id = :session_id
                        ORDER BY id DESC
                        LIMIT 1
                    );
                """),
                {"session_id": session_id},
            )

    async def generate_chat_title(self, chat_id: str) -> str:
        history = await self.get_message_history(chat_id)
        # Get the first two messages of the conversation
        conversation = history[:2]

        # Convert the messages into text for the LLM
        conversation_text = "\n".join(
            f"{message.role}: {message.content}"
            for message in conversation
        )

        title_chain = (
                ChatPromptTemplate.from_messages([
                    (
                        "system",
                        """
                        Generate a chat title based on the conversation below.
    
                        Rules:
                        - Maximum 5 words.
                        - Return only the title.
                        - No quotation marks.
                        - No punctuation at the end.
                        """
                    ),
                    ("human", "{conversation}")
                ])
                | self.llm
                | StrOutputParser()
        )

        title = await title_chain.ainvoke({
            "conversation": conversation_text
        })

        return title

    async def delete_chat(self, session_id: str):
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    DELETE FROM message_store
                    WHERE session_id = :session_id
                """),
                {"session_id": session_id},
            )

    async def get_last_entry(self, session_id: str):
        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT *
                    FROM message_store
                    WHERE id = (
                        SELECT id FROM message_store
                        WHERE session_id = :session_id
                        ORDER BY id DESC
                        LIMIT 1
                    )
                """),
                {"session_id": session_id}
            )
            row = result.first()
            if row:
                return row[2]

    def _get_session_history(self, session_id: str) -> SQLChatMessageHistory:
        return SQLChatMessageHistory(
            session_id=session_id,
            connection=self.engine,
        )

    def _trim(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        if len(messages) > self.max_messages:
            return messages[-self.max_messages:]
        return messages

    def wrap_chain(self, base_chain) -> RunnableWithMessageHistory:
        """
            Wraps a LangChain Runnable with automatic conversation history management.

            The session history is loaded from PostgreSQL, trimmed to the configured
            maximum number of messages (`max_messages`), and injected into the
            `base_chain` before execution. After the model generates a response,
            the new messages are automatically persisted for the current session.

            Args:
                base_chain: The main processing pipeline (e.g., prompt → LLM → parser).

            Returns:
                A `RunnableWithMessageHistory` that automatically retrieves and
                updates the conversation history using the session ID.
        """
        chain = (
                RunnablePassthrough.assign(
                    history=lambda x: self._trim(x["history"])
                )
                | base_chain
        )

        return RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )
