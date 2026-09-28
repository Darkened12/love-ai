from services.context_memory import ContextMemory
from services.message_datetime import MessageDatetime
from services.gateway_bridge import GatewayBridge
from langchain_core.messages import HumanMessage
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
        full_prompt = [
            SystemMessage(content=prompt),
            *[msg.to_lc() for msg in context_history],
            HumanMessage(content="(OOC: Now send the new message to the user.)")
        ]
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
        You are Sofia.

        The user has been away for {time_difference}.

        Below is the previous conversation. Use it only as context.

        IMPORTANT:
        - Generate a NEW message addressed to the USER.
        - Do not reply to your own previous messages.
        - Do not continue speaking as if you were the user.
        - Do not assume the user has just said anything.
        - Start a new conversational turn naturally.
        - The previous assistant message is only context.
        - Return ONLY the message Sofia would send to the user.

        Previous conversation:
        """
        return prompt