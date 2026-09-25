import asyncio
from datetime import datetime, timezone
from services.reply_worker import ReplyWorker
from services.gateway_bridge import GatewayBridge
from services.message_datetime import MessageDatetime

class ReplyScheduler:
    def __init__(self, worker: ReplyWorker):
        self.worker = worker

    async def run(self):
        while True:
            await self._start()
            await asyncio.sleep(30)

    async def _start(self):
        users = await GatewayBridge.get_users_last_message_at()
        extracted_users = self.extract_away_users(users)
        for user in extracted_users:
            user_id = user['id']
            asyncio.create_task(self._process_user(user_id))

    async def _process_user(self, user_id: int):
        await self.worker.process_user(user_id=user_id)

    @staticmethod
    def extract_away_users(users: list[dict]) -> list[dict]:
        away_users = []

        for user in users:
            message_str = user['last_message_at']

            message_datetime = MessageDatetime.parse_api_datetime(message_str)
            now = datetime.now(timezone.utc)
            time_difference = now - message_datetime

            if time_difference.total_seconds() >= 60 * 60:
                away_users.append(user)

        return away_users