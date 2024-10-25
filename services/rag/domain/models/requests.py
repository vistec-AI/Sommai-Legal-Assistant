from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    model: str
    language: str
    top_k: int = 10
    top_n: int = 10
    reranker: bool = True
    temperature: float = 0.5

class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 10
    top_n: int = 10
    reranker: bool = True