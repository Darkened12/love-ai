import random
from services.reply_worker import ReplyWorker

class FollowUp:
    def __init__(self, worker: ReplyWorker):
        self.worker = worker
        self.processing_users: set[int] = set()

    @staticmethod
    def _should_execute() -> bool:
        # 1 in 4
        return random.randrange(0, 4) == 3

    async def process_user(self, user_id: int):
        if not self._should_execute():
            return

        if user_id in self.processing_users:
            return

        self.processing_users.add(user_id)

        try:
            await self.worker.process_user(user_id=user_id)
        finally:
            self.processing_users.remove(user_id)