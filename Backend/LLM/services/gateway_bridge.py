import httpx
from services.context_memory import ContextMemory
from config import GATEWAY_URL

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