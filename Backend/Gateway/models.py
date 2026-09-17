from typing import Optional
from pydantic import BaseModel


class TokenRefreshRequest(BaseModel):
    username: str
    password: str


class TokenAccessRequest(BaseModel):
    refresh: str


class ChatHistoryRequest(BaseModel):
    pass


class MessageRequest(BaseModel):
    user_id: int
    chat_id: str
    message: str
    system_prompt: Optional[str] = None
    tts: bool = False


class RegenerateMessageResponse(BaseModel):
    user_id: int
    chat_id: str
    system_prompt: Optional[str] = None
