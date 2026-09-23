from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from services.gateway_bridge import GatewayBridge

class MessageDatetime:
    @staticmethod
    def parse_api_datetime(value: str) -> datetime:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        elif value.endswith("+00"):
            value = value[:-3] + "+00:00"

        return datetime.fromisoformat(value)

    @staticmethod
    def get_datetime_prompt() -> str:
        now = datetime.now(ZoneInfo("America/Sao_Paulo"))
        return f"""
    Current date and time: {now.strftime("%A, %B %d, %Y, %H:%M")}.
    Timezone: America/Sao_Paulo.
    The user is in Brazil.
        """

    @classmethod
    async def get_time_difference_prompt(cls, user_id: int) -> str:
        message_datetime_string = await GatewayBridge.get_user_last_message_at(user_id)
        message_datetime = cls.parse_api_datetime(message_datetime_string)
        now = datetime.now(timezone.utc)
        time_difference = now - message_datetime

        total_seconds = int(time_difference.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours == 0:
            human_delta = f"{minutes} minutes"
        elif minutes == 0:
            human_delta = f"{hours} hours"
        else:
            human_delta = f"{hours} hours and {minutes} minutes"

        return f"""The user's last message was sent about {human_delta} ago.

    Treat this as real elapsed time. Mention the time gap only if it feels natural in the conversation.
    """