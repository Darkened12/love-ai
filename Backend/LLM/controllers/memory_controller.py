import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from services.context_memory import ContextMemory
from services.persistent_memory import PersistentMemory


class MemoryController:
    def __init__(self, llm: ChatOpenAI):
        self._llm = llm
        self._context_memory = ContextMemory(llm)
        self._persistent_memory = PersistentMemory(llm)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", """{system_prompt}
        {long_term_context}
        {relationship}
        """),
            MessagesPlaceholder("history"),
            ("human", "{input}")
        ])
        _base_chain = self._prompt | llm
        self._base_chain = _base_chain
        self._chain = self._context_memory.wrap_chain(_base_chain)

    @property
    def context_memory(self):
        return self._context_memory

    @property
    def persistent_memory(self):
        return self._persistent_memory

    @property
    def prompt(self):
        return self._prompt

    @property
    def chain(self):
        return self._chain

    @property
    def base_chain(self):
        return self._base_chain
