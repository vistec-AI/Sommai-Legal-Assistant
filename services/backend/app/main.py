import logging
import asyncio
import json
import requests

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from contextlib import asynccontextmanager
from app.rabbitmq.client import RabbitMQBroker
from pydantic import BaseModel
from app.custom_models.models import ChatJobInQueueMessage
from app.processing.process_chat import ChatProcessor

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class StreamingRequest(BaseModel):
    text: str


class Response(BaseModel):
    output: str


async def consume_job(loop, rabbitmq_client):
    while True:
        try:
            incoming_message = await rabbitmq_client.consume()
        except Exception as e:
            print("Failed to consume job:", str(e))
        if incoming_message:
            job_msg = ChatJobInQueueMessage.model_validate_json(incoming_message.body)
            print(
                json.dumps(
                    {
                        "type": "log",
                        "log_level": "INFO",
                        "method": "consume_job",
                        "msg": "Job received",
                        "job_id": job_msg.job_id,
                    }
                )
            )
            try:
                await ChatProcessor.save_chat_history(job_msg.chat_id, job_msg.answer, job_msg.status)
                # Confirm message
                await incoming_message.ack()
            except Exception as e:
                print(
                    json.dumps(
                        {
                            "type": "log",
                            "log_level": "ERROR",
                            "method": "consume_job",
                            "msg": str(e),
                        }
                    )
                )
                # Reject message
                await incoming_message.reject()
        # Sleep for 3 seconds
        await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    print(
        json.dumps(
            {"type": "log", "log_level": "INFO", "msg": "Starting job consumer..."}
        )
    )
    rabbitmq_client = RabbitMQBroker(
        settings.RABBITMQ_HOST,
        settings.RABBITMQ_PORT,
        settings.RABBITMQ_USERNAME,
        settings.RABBITMQ_PASSWORD,
        exchange_name="ex.default",
        queue_name="q.default",
    )
    try:
        await rabbitmq_client.connect(loop)
    except Exception:
        print(
            json.dumps(
                {
                    "type": "log",
                    "log_level": "ERROR",
                    "method": "lifespan",
                    "msg": "Failed to connect to RabbitMQ",
                }
            )
        )
        raise
    print(
        json.dumps({"type": "log", "log_level": "INFO", "msg": "Job consumer started"})
    )
    loop.create_task(consume_job(loop, rabbitmq_client))
    yield
    print(
        json.dumps(
            {
                "type": "log",
                "log_level": "INFO",
                "msg": "Shutting down job consumer...",
            }
        )
    )

app = FastAPI(lifespan=lifespan)

origins = [
    "*"
]

app.include_router(api_router, prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
