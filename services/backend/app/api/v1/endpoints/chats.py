import json
import os
from typing import Any, List, Optional
from uuid import UUID
from pydantic import UUID4
from app import crud, models, schemas
from app.api import deps
from app.models.chat_room import ChatRoom
from app.models.inference_model import InferenceModel
from typing import AsyncGenerator
from sse_starlette.sse import EventSourceResponse
from app.core.config import settings
from enum import Enum
from urllib.parse import urljoin
from app.utils_func.streaming import fetch_answer_stream, filter_other_lang, escape_inner_quotes
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
    BackgroundTasks,
    Request
)
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import asyncio
from app.rabbitmq.client import RabbitMQBroker
from app.custom_models.models import ChatJobInQueueMessage
from app.custom_models.models import ModelResponseStatus
from app.custom_models.models import LawReference
from pydantic import BaseModel

class ChatRetrieval(BaseModel):
  chat_id: UUID4
  inference_model_id: UUID4
  question: str

class ChatRetrievalResponse(BaseModel):
  law_references: Optional[List[LawReference]] = None

router = APIRouter(route_class=AuthenticatedRoute)

rabbitmq_client = RabbitMQBroker(
    settings.RABBITMQ_HOST,
    settings.RABBITMQ_PORT,
    settings.RABBITMQ_USERNAME,
    settings.RABBITMQ_PASSWORD,
    exchange_name="ex.default",
    queue_name="q.default",
)


MESSAGE_STREAM_DELAY = 0.01 # 1 milliseconds
MESSAGE_STREAM_RETRY_TIMEOUT = 3000  # milliseconds


def chat_room_exists(db: Session, chat_room_id: UUID4) -> bool:
    return db.query(ChatRoom).filter(ChatRoom.id == chat_room_id).first() is not None

def inference_model_exists(db: Session, inference_model_id: UUID4) -> bool:
    return db.query(InferenceModel).filter(InferenceModel.id == inference_model_id).first() is not None

@router.get("/", response_model=List[schemas.Chat])
def read_chats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    skip: int = 0,
    limit: int = 10000,
    chat_room_id: UUID = UUID(int=0)
) -> Any:
    if chat_room_id == UUID(int=0):
        chat = crud.chat.list_all(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        chat = crud.chat.list_by_chat_room_id(
            db=db, user_id=current_user.id, chat_room_id=chat_room_id , skip=skip, limit=limit
        )

    chat.sort(key=lambda x: x.created_at, reverse=True)

    return chat

@router.get("/chat/{id}", response_model=schemas.Chat)
def read_chat(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID
) -> Any:
    chat = crud.chat.get(db=db, id=id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat not found"
            }
        )
    return chat

def save_chat_history(
    db: Session, chat_id: UUID4, complete_answer: str, status: str
):
    chat_in = schemas.ChatUpdate(answer=complete_answer, status=status)
    chat = crud.chat.get(db=db, id=chat_id)
    if chat:
        crud.chat.update(db=db, db_obj=chat, obj_in=chat_in)

async def submit_job_to_rabbitmq(loop, chat_id: UUID4, answer: str, status: str):
    print("Submit a job to queue...", answer, status)
    """Submit a job to queue"""
    # Generate job id as UUID4
    job_id = str(uuid.uuid4()).replace("-", "")
    try:
        await rabbitmq_client.connect(loop)
        await rabbitmq_client.publish(
            ChatJobInQueueMessage(job_id=job_id, chat_id=chat_id, answer=answer, status=status)
        )
    except Exception:
        print("Failed to submit job to RabbitMQ")


@router.post("/retrieval", response_model=ChatRetrievalResponse)
async def retrieval_law_reference(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    request: Request,
    background_tasks: BackgroundTasks,
    chat_retrieval_in: ChatRetrieval,
) -> Any:
    chat = crud.chat.get(db=db, id=chat_retrieval_in.chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat not found"
            }
        )
    inference_model = crud.inference_model.get(db=db, id=chat_retrieval_in.inference_model_id)
    if inference_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference model not found"
            }
        )
    domain = inference_model.domain
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference domain not found"
            }
        )
    base_url = f"http://{domain}"
    url = urljoin(base_url, "retrieval")
    payload ={
        "query": chat_retrieval_in.question,
        "top_k": 10,
        "top_n": 5,
        "reranker": True
    }
    headers = {"Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response_retrieval = await client.post(url, headers=headers, json=payload)
            response_status_code = response_retrieval.status_code
            law_references = None
            if response_status_code == 200:
                try:
                    law_references = response_retrieval.json()
                except ValueError:
                    law_references = None

            chat_update_in = schemas.ChatUpdate(law_references=law_references)
            updated_chat = crud.chat.update(db=db, db_obj=chat, obj_in=chat_update_in)
            return {"law_references": law_references}
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Request timed out: {exc}"
            }
        )
    except httpx.ConnectTimeout as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "connection_error",
                "description": f"Error: {str(exc.response.text)}"
            }
        )
    except httpx.ReadTimeout as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Request timed out: {exc}"
            }
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "http_error",
                "description": f"HTTP error occurred: {exc.response.status_code}"
            }
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "connection_error",
                "description": f"Connection error: {exc}"
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": f"Internal server error: {exc}"
            }
        )


# create a chat then ask question to the model and update answer to the chat
@router.post("/question", response_class=EventSourceResponse)
async def create_chat(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    request: Request,
    background_tasks: BackgroundTasks,
    chat_in: schemas.ChatCreate,
) -> Any:
    question = chat_in.question
    chat_room_id = chat_in.chat_room_id
    inference_model_id = chat_in.inference_model_id
    if not chat_room_exists(db=db, chat_room_id=chat_room_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat room not found"
            }
        )
    inference_model = crud.inference_model.get(db=db, id=inference_model_id)
    if inference_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference model not found"
            }
        )
    chat_in = schemas.ChatCreate(question=question, chat_room_id=chat_room_id, inference_model_id=inference_model_id)

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

    base_url = f"http://{domain}"
    url = urljoin(base_url, "generate")
    loop = asyncio.get_event_loop()
    payload = {
        "query": question,
        "model": inference_model.llm_name,
        "language": "th",
        "top_k": 10,
        "top_n": 5,
        "reranker": True,
        "temperature": 0.5,
    }
    headers = {
        "Content-Type": "application/json"
    }
    new_chat = crud.chat.create(
        db=db, obj_in=chat_in, user_id=current_user.id
    )

    async def submit_failed_chat():
        save_chat_history(db, new_chat.id, "", ModelResponseStatus.FAILED)
        await submit_job_to_rabbitmq(loop, new_chat.id, "", ModelResponseStatus.FAILED)

    try:
        async def stream_model_data():
            async with httpx.AsyncClient(timeout=120) as client:
                buffer = ""
                try:
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        try:
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
                        except Exception as e:
                            print(f"Unexpected error during streaming: {str(e)}")

                except httpx.RequestError as exc:
                    print(f"Error contacting model: {exc}")
                    await submit_failed_chat()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "code": "connection_error",
                            "description": f"Connection error: {exc}"
                        }
                    )
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
    except httpx.TimeoutException as exc:
        print(f"Request timed out: {exc}")
        await submit_failed_chat()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Request timed out: {exc}"
            }
        )
    except httpx.ConnectTimeout as exc:
        print(f"Connection to the server timed out: {exc}")
        await submit_failed_chat()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Connection to the server timed out: {exc}"
            }
        )
    except httpx.ReadTimeout as exc:
        print(f"Server response read timeout: {exc}")
        await submit_failed_chat()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "timeout_error",
                "description": f"Server response read timeout: {exc}"
            }
        )
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error occurred: {exc.response.status_code}")
        await submit_failed_chat()
        raise HTTPException(
            status_code=exc.response.status_code,
            detail={
                "code": "http_status_error",
                "description": f"HTTP error occurred: {exc.response.status_code}"
            }
        )
    except httpx.StreamError as exc:
        print(f"Stream error occurred: {exc}")
        await submit_failed_chat()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "connection_error",
                "description": f"Stream error occurred: {exc}"
            }
        )
    except httpx.RequestError as exc:
        await submit_failed_chat()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "connection_error",
                "description": f"Connection error: {exc}"
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        await submit_failed_chat()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": "Internal server error"
            }
        )
    try:

        collected_answer = []
        model_status = ModelResponseStatus.DONE
        async def event_publisher():
            nonlocal model_status
            try:
                async for chunk in stream_model_data():
                    filtered_chunk = filter_other_lang(chunk)
                    collected_answer.append(filtered_chunk)
                    yield {"data": {"text": filtered_chunk, "chat_id": str(new_chat.id)}, "retry": MESSAGE_STREAM_RETRY_TIMEOUT}
                    await asyncio.sleep(MESSAGE_STREAM_DELAY)
            except HTTPException as http_exc:
                if len(collected_answer) <= 0:
                    model_status =  ModelResponseStatus.FAILED
                yield {"event": "error", "data": {"code": "error", "description": str(http_exc.detail)}}
            except Exception as exc:
                if len(collected_answer) <= 0:
                    model_status =  ModelResponseStatus.FAILED
                yield {"event": "error", "data": {"code": "error", "description": str(exc)}}
            finally:
                complete_answer = ''.join(collected_answer)
                background_tasks.add_task(save_chat_history, db, new_chat.id, complete_answer, model_status)
                background_tasks.add_task(submit_job_to_rabbitmq, loop, new_chat.id, complete_answer, model_status)
        return EventSourceResponse(event_publisher())
    except HTTPException as http_exc:
        raise http_exc
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
        await asyncio.sleep(0.1)

@router.put("/{id}", response_model=schemas.Chat)
def update_chat(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    chat_in: schemas.ChatUpdate,
) -> Any:
    chat = crud.chat.get(db=db, id=id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat not found"
            }
        )
    chat = crud.chat.update(db=db, db_obj=chat, obj_in=chat_in)
    return chat

@router.delete("/{id}", response_model=schemas.Chat)
def delete_chat(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    chat = crud.chat.get(db=db, id=id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat not found"
            }
        )
    chat = crud.chat.remove(db=db, id=id)
    return chat
