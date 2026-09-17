from typing import Optional

from dotenv import load_dotenv
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel

load_dotenv('.env')


class ChatRequest(BaseModel):
    user_id: int
    chat_id: str
    message: str
    system_prompt: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

    def to_lc(self):
        if self.role == "user":
            return HumanMessage(content=self.content)
        elif self.role == "assistant":
            return AIMessage(content=self.content)
        else:
            raise ValueError(f"Invalid role: {self.role}")


class RegenerateResponseRequest(BaseModel):
    user_id: int
    chat_id: str
    system_prompt: Optional[str] = None


class MemoryMetadata(BaseModel):
    user_id: str
    fact_id: str
    created_at: str | None = None


class Memory(BaseModel):
    id: str
    fact: str
    metadata: MemoryMetadata
