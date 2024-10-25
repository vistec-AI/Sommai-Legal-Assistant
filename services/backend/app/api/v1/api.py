from fastapi import APIRouter

from app.api.v1.endpoints import chat_rooms, ping, chats, inference_models, arena, arena_model_responses, authentication, rating

api_router = APIRouter()
api_router.include_router(ping.router, tags=["ping"])

api_router.include_router(chat_rooms.router, prefix="/chat-rooms", tags=["chat_rooms"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(inference_models.router,  prefix="/inference-models", tags=["inference_models"])
api_router.include_router(arena.router, prefix="/arena", tags=["arena"])
api_router.include_router(arena_model_responses.router, prefix="/arena-model-responses", tags=["arena_model_responses"])
api_router.include_router(authentication.router, prefix="/auth", tags=["auth"])
api_router.include_router(authentication.auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(rating.router, prefix="/rating", tags=["rating"])