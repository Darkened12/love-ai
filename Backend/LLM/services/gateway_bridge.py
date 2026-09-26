import httpx
from services.context_memory import ContextMemory
from config import GATEWAY_URL
from datetime import datetime

class GatewayBridge:
    @staticmethod
    async def generate_title(context_memory: ContextMemory, user_id: int, chat_id: str) -> str:
        title = await context_memory.generate_chat_title(chat_id)
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

    @staticmethod
    async def get_user_last_message_at(user_id: int) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GATEWAY_URL}/internal/get_user_last_message_at",
                params={
                    "user_id": user_id
                }
            )

            content = response.json()
            return content['last_message_at']

    @staticmethod
    async def get_users_last_message_at() -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/internal/get_users_last_message_at")
            return response.json()

    @staticmethod
    async def get_last_chat(user_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GATEWAY_URL}/internal/get_last_chat",
                params={
                    "user_id": user_id
                }
            )

            return response.json()


    @staticmethod
    async def update_chat_date(user_id: int, chat_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{GATEWAY_URL}/internal/update_chat_date",
                params={
                    "user_id": user_id,
                    "chat_id": chat_id
                }
            )

            return response

    @staticmethod
    async def reply(
            user_id: int,
            chat_id: str,
            role: str,
            message_id: int,
            message: str,
            timestamp: datetime
    ):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GATEWAY_URL}/internal/reply",
                json={
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "role": role,
                    "message_id": message_id,
                    "message": message,
                    "timestamp": timestamp
                }
            )

            response.raise_for_status()