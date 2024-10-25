import json
import os
from typing import Any, List, Optional
from uuid import UUID
from pydantic import UUID4
import uuid
from app import crud, models, schemas
from app.api import deps
from app.models.arena import Arena
from app.models.inference_model import InferenceModel
from sse_starlette.sse import EventSourceResponse
from urllib.parse import urljoin
from app.custom_models.models import ModelResponseStatus, LawReference
import asyncio
from app.api.custom_route import AuthenticatedRoute

import requests, uuid, json
import httpx

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Request,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils_func.streaming import fetch_answer_stream, filter_other_lang, escape_inner_quotes

router = APIRouter(route_class=AuthenticatedRoute)

MESSAGE_STREAM_DELAY = 0.001 # 1 milliseconds
MESSAGE_STREAM_RETRY_TIMEOUT = 3000  # milliseconds

@router.get("/", response_model=List[schemas.ArenaModelResponse])
def read_arena_model_responses(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    skip: int = 0,
    limit: int = 10000,
    arena_id: UUID = UUID(int=0)
) -> Any:
    if arena_id == UUID(int=0):
        arena_model_response = crud.arena_model_response.list_all(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        arena_model_response = crud.arena_model_response.list_by_arena_id(
            db=db, user_id=current_user.id, arena_id=arena_id , skip=skip, limit=limit
        )

    arena_model_response.sort(key=lambda x: x.created_at, reverse=True)

    return arena_model_response

@router.get("/arena-model-response/{id}", response_model=schemas.ArenaModelResponse)
def read_arena_model_response(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID
) -> Any:
    arena_model_response = crud.arena_model_response.get(db=db, id=id)
    if not arena_model_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Arena model response not found"
            }
        )
    return arena_model_response

def save_arena_model_response_history(
    db: Session, arena_model_response_id: UUID4, complete_answer: str, status: str, law_references: Optional[List[LawReference]] = None
):
    arena_model_response_in = schemas.ArenaModelResponseUpdate(answer=complete_answer, status=status, law_references=law_references)
    arena_model_response = crud.arena_model_response.get(db=db, id=arena_model_response_id)
    if arena_model_response:
        updated_arena_model_response = crud.arena_model_response.update(db=db, db_obj=arena_model_response, obj_in=arena_model_response_in)
        return updated_arena_model_response
    else:
        return None

def arena_exists(db: Session, arena_id: UUID4) -> bool:
    return db.query(Arena).filter(Arena.id == arena_id).first() is not None

def inference_model_exists(db: Session, inference_model_id: UUID4) -> bool:
    return db.query(InferenceModel).filter(InferenceModel.id == inference_model_id).first() is not None

async def get_law_references(base_url: str, llm_name: str, question: str) -> Any:
    law_references = None
    retrieval_url = urljoin(base_url, "retrieval")
    retrieval_payload = {
        "query": question,
        "top_k": 10,
        "top_n": 5,
        "reranker": True
    }
    
    headers = {"Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response_retrieval = await client.post(retrieval_url, headers=headers, json=retrieval_payload)
            response_status_code = response_retrieval.status_code
            law_references = None
            if response_status_code == 200:
                try:
                    law_references = response_retrieval.json()
                except ValueError:
                    law_references = None
            return law_references
    except httpx.TimeoutException as exc:
        print(f"Request timed out: {exc}")
        return None
    except httpx.ConnectTimeout as exc:
        print(f"Connection to the server timed out: {exc}")
        return None
    except httpx.ReadTimeout as exc:
        print(f"Server response read timeout: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error occurred: {exc.response.status_code}")
        return None
    except httpx.StreamError as exc:
        print(f"Stream error occurred: {exc}")
        return None
    except httpx.RequestError as exc:
        print(f"Connection error: {exc}")
        return None
    except Exception as exc:
        return None

# create a arena model response then ask question to the model and update answer to the arena model response by id
@router.post("/question", response_model=schemas.ArenaModelResponse)
async def create_arena_model_response(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    request: Request,
    background_tasks: BackgroundTasks,
    arena_model_response_in: schemas.ArenaModelResponseCreate,
) -> Any:
    if not arena_exists(db=db, arena_id=arena_model_response_in.arena_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Arena not found"
            }
        )

    inference_model = db.query(InferenceModel).filter(InferenceModel.id == arena_model_response_in.inference_model_id).first()
    if inference_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference model not found"
            }
        )

    # model url
    domain = inference_model.domain
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference domain not found"
            }
        )

    new_arena_model_response = crud.arena_model_response.create(
        db=db, obj_in=arena_model_response_in, user_id=current_user.id
    )

    base_url = f"http://{domain}"
    url = urljoin(base_url, "generate")

    payload = {
        "query": arena_model_response_in.question,
        "model": inference_model.llm_name,
        "language": "th",
        "top_k": 10,
        "top_n": 5,
        "reranker": True,
        "temperature": 0.5
    }
    headers = {"Content-Type": "application/json"}

    def save_failed_arena_model_response():
        updated_arena_model_response =  save_arena_model_response_history(db=db, arena_model_response_id=new_arena_model_response.id, complete_answer=None, status=ModelResponseStatus.FAILED, law_references=None)
        if updated_arena_model_response is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "internal_server_error",
                    "description": "Internal server error"
                }
            )

    try:
        async def stream_model_data():
            async with httpx.AsyncClient(timeout=120) as client:
                buffer = ""
                try:
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        async for chunk in response.aiter_bytes():
                            if chunk:
                                chunk_data = chunk.decode("utf-8")
                                buffer += chunk_data
                                try:
                                    escaped_text = escape_inner_quotes(buffer)
                                    chunk_json_obj = json.loads(escaped_text, strict=False)
                                    buffer = ""
                                    if "text" in chunk_json_obj:
                                        yield chunk_json_obj["text"]
                                    else:
                                        yield ""
                                except json.JSONDecodeError:
                                    yield ""
                                except (ValueError, KeyError):
                                    yield ""
                except httpx.RequestError as exc:
                    save_failed_arena_model_response()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "code": "connection_error",
                            "description": f"Connection error: {exc}"
                        }
                    )
    except httpx.TimeoutException as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Request timed out: {exc}"
            }
        )
    except httpx.ConnectTimeout as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Connection to the server timed out: {exc}"
            }
        )
    except httpx.ReadTimeout as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Server response read timeout: {exc}"
            }
        )
    except httpx.HTTPStatusError as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=exc.response.status_code,
            detail={
                "code": "http_status_error",
                "description": f"HTTP error occurred: {exc.response.status_code}"
            }
        )
    except httpx.StreamError as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "connection_error",
                "description": f"Stream error occurred: {exc}"
            }
        )
    except httpx.RequestError as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "connection_error",
                "description": f"Connection error: {exc}"
            }
        )
    except Exception as exc:
        await save_failed_arena_model_response()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": "Internal server error"
            }
        )

    loop = asyncio.get_event_loop()
    collected_answer = []
    law_references = None
    model_status = ModelResponseStatus.DONE
    try:
        async for chunk in stream_model_data():
            filtered_chunk = filter_other_lang(chunk)
            collected_answer.append(filtered_chunk)
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

        complete_answer = ''.join(collected_answer)
        if "สมหมายไม่สามารถตอบคำถามนี้" not in complete_answer:
            law_references_response = await get_law_references(base_url=base_url, llm_name=inference_model.llm_name, question=arena_model_response_in.question)
            if law_references_response is not None:
                law_references = law_references_response
        updated_arena_model_response =  save_arena_model_response_history(db=db, arena_model_response_id=new_arena_model_response.id, complete_answer=complete_answer, status=ModelResponseStatus.DONE, law_references=law_references)
        if updated_arena_model_response is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "internal_server_error",
                    "description": "Internal server error"
                }
            )
        return updated_arena_model_response

    except HTTPException as exc:
        raise exc
    except Exception as exc:
        print(f"An unexpected error occurred while streaming: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": f"An unexpected error occurred while streaming: {exc}"
            }
        )

# mock streaming
async def mock_paragraph():
    # Example paragraph to send as stream events
    paragraph = "Green tea comes from unoxidized leaves of the Camellia sinensis bush. It is one of the least processed types of tea, containing the most antioxidants and beneficial polyphenols. Some research suggests green tea may positively affect weight loss, liver disorders, type 2 diabetes, Alzheimer’s disease, and more. However, more evidence is necessary for researchers to definitively prove these health benefits. This article lists some potential health benefits and types of green tea, its nutrition content, and the potential side effects."

    # Split the paragraph into words
    words = paragraph.split()
    collected_answer = []
    for word in words:
        yield word + " "
        await asyncio.sleep(MESSAGE_STREAM_DELAY)

@router.put("/{id}", response_model=schemas.ArenaModelResponse)
def update_arena_model_response(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    arena_model_response_in: schemas.ArenaModelResponseUpdate,
) -> Any:
    arena_model_response = crud.arena_model_response.get(db=db, id=id)
    if not arena_model_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Arena model response not found"
            }
        )
    arena_model_response = crud.arena_model_response.update(db=db, db_obj=arena_model_response, obj_in=arena_model_response_in)
    return arena_model_response

@router.delete("/{id}", response_model=schemas.ArenaModelResponse)
def delete_arena_model_response(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    arena_model_response = crud.arena_model_response.get(db=db, id=id)
    if not arena_model_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Arena model response not found"
            }
        )
    arena_model_response = crud.arena_model_response.remove(db=db, id=id)
    return arena_model_response
