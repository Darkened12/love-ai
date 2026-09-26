from services.context_memory import ContextMemory
from services.message_datetime import MessageDatetime
from services.gateway_bridge import GatewayBridge
from models.models import MessageResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from datetime import datetime, timezone

class ReplyWorker:
    def __init__(self, context_memory: ContextMemory, llm: ChatOpenAI):
        self.context_memory = context_memory
        self.llm = llm

    async def process_user(self, user_id: int):
        last_chat = await GatewayBridge.get_last_chat(user_id) # 'chat_id' and 'last_message_at'
        context_history = await self.context_memory.get_message_history(last_chat['chat_id'])

        prompt = await self._build_prompt(user_id)
        full_prompt = [SystemMessage(content=prompt), *[msg.to_lc() for msg in context_history]]
        message = await self.llm.ainvoke(full_prompt)

        added_message = await self.context_memory.append_message(last_chat['chat_id'], 'assistant', message.content)

        await GatewayBridge.update_chat_date(user_id, last_chat['chat_id'])
        await GatewayBridge.reply(
            user_id=user_id,
            chat_id=last_chat['chat_id'],
            role='assistant',
            message_id=added_message.id,
            message=added_message.content,
            timestamp=added_message.timestamp.isoformat()
        )

    async def _build_prompt(self, user_id: int):
        time_difference = await MessageDatetime.get_time_difference_prompt(user_id)
        prompt = f"""
        # Important
        Return a message based on the conversation below. Keep in mind the time that has passed: 
        {time_difference}
        """
        return prompt