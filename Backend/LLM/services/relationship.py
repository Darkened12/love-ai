import json
from langchain_openai import ChatOpenAI

from controllers.relationship_controller import RelationshipController
from models.user_relationship import UserRelationship


class RelationshipService:
    def __init__(self, llm: ChatOpenAI, controller: RelationshipController):
        self.llm = llm
        self.controller = controller

    async def evaluate_and_save(self, user_id: int, user_message: str, assistant_message: str) -> UserRelationship | None:
        prompt = f"""
You are a relationship state evaluator.

Analyze ONLY this exchange between the user and Sofia.

Return ONLY valid JSON.

Rules:
- affection: integer from -5 to 5
- trust: integer from -5 to 5
- comfort: integer from -5 to 5
- Use 0 when there is no meaningful change.
- Do not explain your reasoning.
- Output only JSON.

User:
{user_message}

Sofia:
{assistant_message}
"""
        result = await self.llm.ainvoke(prompt)

        try:
            decoded_result = json.loads(result.content)
        except json.JSONDecodeError:
            return

        return await self.controller.modify_relationship(user_id, decoded_result)
