import asyncio
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List

from config import GATEWAY_URL
from controllers.relationship_controller import RelationshipController
from models.user_relationship import Base
from services.relationship import RelationshipService

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_openai import ChatOpenAI

from controllers.memory_controller import MemoryController
from models.models import ChatRequest, MessageResponse, RegenerateResponseRequest, Memory

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_api_key = os.getenv('OPENAI_API_KEY')
if _api_key is None:
    _api_key = os.getenv('DEEPSEEK_BOT_KEY')

_llm = ChatOpenAI(
    openai_api_base=os.getenv('BASE_URL'),
    openai_api_key=_api_key,
    model=os.getenv('MODEL'),
    streaming=False,
    max_tokens=int(os.getenv('MAX_TOKENS')),
    temperature=float(os.getenv('TEMPERATURE')),
)

_memory_controller = MemoryController(_llm)
_relationship_controller = RelationshipController(
    dsn=f"postgresql+asyncpg://postgres:{os.getenv('POSTGRES_PASSWORD')}@db:5432/user_relationship",
    base_class=Base
)
_relationship_service = RelationshipService(llm=_llm, controller=_relationship_controller)


async def generate_title(user_id: int, chat_id: str) -> str:
    title = await _memory_controller.context_memory.generate_chat_title(chat_id)
    async with httpx.AsyncClient() as client:
        await client.patch(
            f'{GATEWAY_URL}/internal/create_chat_title',
            params={
                'chat_id': chat_id,
                "user_id": user_id,
                "title": title
            }
        )

    return title


def get_datetime_prompt() -> str:
    now = datetime.now(ZoneInfo("America/Sao_Paulo"))
    return f"""
Current date and time: {now.strftime("%A, %B %d, %Y, %H:%M")}.
Timezone: America/Sao_Paulo.
The user is in Brazil.
    """


async def regenerate_response(user_id: int, chat_id: str, system_prompt: Optional[str]):
    """
    Regenerates an user message by deleting the last entry and updating the context_memory

    :param user_id: The user id on the database
    :param chat_id: The number in str format of the entry
    :param system_prompt: (Optional) System prompt
    """
    await _memory_controller.context_memory.delete_last_entry(chat_id)
    message = await _memory_controller.context_memory.get_last_entry(chat_id)

    full_response = ''
    async for chunk in stream_response(
            message=message,
            user_id=user_id,
            chat_id=chat_id,
            system_prompt=system_prompt,
            manual_history=True
    ):
        yield chunk
        full_response += chunk

    await _memory_controller.context_memory.append_message(
        session_id=chat_id,
        role='assistant',
        content=full_response
    )


async def stream_response(
        message: str,
        chat_id: str,
        user_id: int,
        system_prompt: Optional[str] = None,
        manual_history: Optional[bool] = False):
    """
    Retrieves long-term-memory,

    :param message: input message
    :param chat_id: either user_id or another key to access persistent_memory
    :param user_id: user's database id
    :param system_prompt: self explanatory
    :param manual_history: wether the chat history is necessary or not
    """
    # Retrieve long-term memory
    long_term_context = await _memory_controller.persistent_memory.retrieve(chat_id, message)

    # Retrieve relationship
    relationship = await _relationship_controller.get_or_create_relationship(user_id)

    # Prompt building
    if system_prompt is None:
        system_prompt = os.environ.get("DEFAULT_SYSTEM_PROMPT")

    long_term_memory_prompt = os.environ.get("DEFAULT_LONG_TERM_MEMORY_PROMPT")
    datetime_prompt = get_datetime_prompt()

    prompt = f"""
    [Runtime Context]
    {datetime_prompt}
    
    [System Prompt]
    {system_prompt}
    
    [Facts About User]
    {long_term_memory_prompt}
    """

    if relationship is not None:
        relationship_context = f"""
        [Relationship State]
    
        Affection: {relationship.affection}/100
        Trust: {relationship.trust}/100
        Comfort: {relationship.comfort}/100
    
        Higher affection means stronger emotional attachment.
        Higher trust means greater willingness to be vulnerable.
        Higher comfort means more relaxed and spontaneous interactions.
    
        Do not mention these values to the user.
        """
    else:
        relationship_context = ''

    # Stream response
    full_response = ""

    if manual_history:
        history = await _memory_controller.context_memory.get_message_history(chat_id)
        history = [msg.to_lc() for msg in history]
        async for chunk in _memory_controller.base_chain.astream(
                {
                    "input": message,
                    "history": history,
                    "long_term_context": long_term_context,
                    "relationship": relationship_context,
                    "system_prompt": prompt
                },
                config={"configurable": {"session_id": chat_id}},
        ):
            if chunk.content:
                yield chunk.content
                full_response += chunk.content

        history = await _memory_controller.context_memory.get_message_history(chat_id)
        if len(history) == 2:
            title = await generate_title(user_id, chat_id)
            yield f"__TITLE__:{title}"
    else:
        async for chunk in _memory_controller.chain.astream(
                {
                    "input": message,
                    "long_term_context": long_term_context,
                    "relationship": relationship_context,
                    "system_prompt": prompt
                },
                config={"configurable": {"session_id": chat_id}},
        ):
            if chunk.content:
                yield chunk.content
                full_response += chunk.content

        history = await _memory_controller.context_memory.get_message_history(chat_id)
        if len(history) == 2:
            title = await generate_title(user_id, chat_id)
            yield f"__TITLE__:{title}"

    # Store persistent memory automatically
    await _memory_controller.persistent_memory.store_if_relevant(
        user_id, message + "\nAssistant: " + full_response
    )

    # Update relationship
    print(f"before evaluate: '{relationship}'", flush=True)
    updated_relationship = await _relationship_service.evaluate_and_save(user_id, message, full_response)
    print(f"after evaluate: '{updated_relationship}'", flush=True)


@app.on_event('startup')
async def startup():
    await _memory_controller.context_memory.init()
    await _relationship_controller.init()


# ---- Routes ----
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/fetch_chat_history")
async def get_chat(request: Request) -> List[MessageResponse]:
    chat_id = request.query_params.get('chat_id')
    return await _memory_controller.context_memory.get_message_history(chat_id)


@app.post("/fetch_message")
async def stream_chat(req: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_response(
            message=req.message,
            user_id=req.user_id,
            chat_id=req.chat_id,
            system_prompt=req.system_prompt
        ),
        media_type="text/plain",
    )


@app.post("/regenerate_message")
async def regenerate_chat(req: RegenerateResponseRequest) -> StreamingResponse:
    return StreamingResponse(
        regenerate_response(
            user_id=req.user_id,
            chat_id=req.chat_id,
            system_prompt=req.system_prompt
        ),
        media_type="text/plain",
    )


@app.delete("/delete_chat")
async def delete_chat(request: Request):
    chat_id = request.query_params.get('chat_id')
    await _memory_controller.context_memory.delete_chat(chat_id)
    return Response(status_code=204)


@app.get('/get_facts_list')
async def get_facts(request: Request) -> List[Memory]:
    user_id = request.query_params.get('user_id')
    return await _memory_controller.persistent_memory.list_all(user_id)


@app.delete('/delete_memory')
async def delete_memory(request: Request) -> Response:
    memory_id = request.query_params.get("id")

    if not memory_id:
        return Response(
            content="Missing memory id",
            status_code=400
        )

    await asyncio.to_thread(
        _memory_controller.persistent_memory.vector_store.delete,
        ids=[memory_id]
    )

    return Response(status_code=204)

@app.get('/get_relationship')
async def get_relationship(request: Request):
    user_id = request.query_params.get('user_id')

    if user_id is None:
        raise HTTPException(400, "user_id is required")

    relationship = await _relationship_controller.get_or_create_relationship(int(user_id))

    if relationship is None:
        raise HTTPException(404, "Relationship not found")

    return {
        "affection": relationship.affection,
        "trust": relationship.trust,
        "comfort": relationship.comfort
    }

@app.delete('/reset_relationship')
async def reset_relation(request: Request) -> Response:
    user_id = request.query_params.get('user_id')
    result = await _relationship_controller.reset_relationship(int(user_id))
    if result:
        return Response(status_code=204)
    return Response(status_code=404)
