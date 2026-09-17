import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from models.models import Memory


class PersistentMemory:

    def __init__(self, llm):
        self.llm = llm

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        base_dir = Path(__file__).resolve().parents[1]
        persist_dir = base_dir / ".databases" / "long_term_memory"

        self.vector_store = Chroma(
            collection_name="long_term_memory",
            embedding_function=self.embeddings,
            persist_directory=str(persist_dir),
        )

    def _normalize_fact(self, fact: str) -> str:
        return " ".join(fact.lower().split())

    def _fact_id(self, user_id: str, fact: str) -> str:
        raw = f"{user_id}:{self._normalize_fact(fact)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def list_all(self, user_id: str):
        user_id = str(user_id)

        results = await asyncio.to_thread(
            self.vector_store.get,
            where={"user_id": user_id},
        )

        memories = [
            Memory(
                id=id_,
                fact=doc,
                metadata=meta
            )
            for id_, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]

        memories.sort(key=lambda m: m.metadata.created_at or "")

        return memories

    async def extract_facts(self, message: str) -> str:
        prompt = f"""
Extract durable long-term facts about the user ONLY if they are explicitly stated
in the message below.

Do NOT infer from previous knowledge.
Do NOT repeat known facts.
Do NOT guess.

Return ONLY valid JSON.

Format:
{{
  "identity_info": [],
  "stable_preferences": [],
  "goals": [],
  "ongoing_projects": [],
  "personal_traits": []
}}

If nothing durable exists, return: NONE

Message:
{message}
"""

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def store_if_relevant(self, user_id: str, message: str) -> str | None:
        user_id = str(user_id)

        facts = await self.extract_facts(message)
        if facts == "NONE":
            return

        try:
            data = json.loads(facts)
        except json.JSONDecodeError:
            print("Invalid JSON returned by LLM.", flush=True)
            return

        for category, values in data.items():
            if not isinstance(values, list):
                continue

            for fact in values:
                fact = fact.strip()

                if not fact:
                    continue

                fact_id = self._fact_id(user_id, fact)

                existing = await asyncio.to_thread(
                    self.vector_store.get,
                    ids=[fact_id]
                )

                if existing.get("documents"):
                    continue

                await asyncio.to_thread(
                    self.vector_store.add_texts,
                    [fact],
                    metadatas=[{
                        "user_id": user_id,
                        "fact_id": fact_id,
                        "category": category,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }],
                    ids=[fact_id],
                )

    async def retrieve(self, user_id: str, query: str, k: int = 5) -> str:
        user_id = str(user_id)

        docs = await asyncio.to_thread(
            self.vector_store.similarity_search,
            query,
            k,
            filter={"user_id": user_id}
        )

        return "\n".join(d.page_content for d in docs)