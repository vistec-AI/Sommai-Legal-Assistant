import requests
import asyncio
import json
import os
from typing import Any, List
from pydantic.v1 import PrivateAttr
from llama_index.core.embeddings import BaseEmbedding

class InstructorEmbeddings(BaseEmbedding):
    _url: str = PrivateAttr()
    _instruction: str = PrivateAttr()

    def __init__(
        self,
        url: str = os.getenv("EMBEDDING_URL", "http://10.204.100.78:31000/embed"),
        instruction: str = "Represent a document for semantic search:",
        **kwargs: Any,
    ) -> None:
        self._url = url
        self._instruction = instruction
        super().__init__(**kwargs)

    @classmethod
    def class_name(cls) -> str:
        return "instructor"

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return await self._aget_text_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return await asyncio.to_thread(self._get_text_embedding, text)

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._get_text_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        payload = {
            "inputs": text
        }
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self._url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            embedding = response.json()
            return embedding[0]
        else:
            raise Exception(f"Failed to get embedding: {response.text}")

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await asyncio.to_thread(self._get_text_embeddings, texts)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = self._get_text_embedding(text)
            embeddings.append(embedding)
        return embeddings