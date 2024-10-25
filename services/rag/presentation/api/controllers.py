from fastapi import APIRouter, HTTPException
from domain.models.requests import QueryRequest, RetrievalRequest
from adapters.llama_index_adapter import LlamaIndexAdapter

router = APIRouter()
llama_index_adapter = LlamaIndexAdapter()
llama_index_adapter.initialize_retrievers()

@router.post("/retrieval")
async def retrieve_documents(request: RetrievalRequest):
    try:
        return llama_index_adapter.retrieve_documents(request)
    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_response(request: QueryRequest):
    try:
        return llama_index_adapter.generate_response(request)
    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/healthz")
async def health_check():
    return {"status": "ok"}
