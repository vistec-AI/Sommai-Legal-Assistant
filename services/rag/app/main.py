from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import traceback
import logging
import time
import json
from presentation.api.controllers import router as api_router

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
        }
        log.update(getattr(record, "msg", {}))
        return json.dumps(log)


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn.error").disabled = True


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        log = {
            "http.status": None,
            "http.method": request.method,
            "http.host": request.url.hostname,
            "http.path": request.url.path,
            "http.headers": dict(request.headers),
        }
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            log["http.status"] = response.status_code
            log["latency"] = process_time
            logger.info(log)
        except:
            log["http.status"] = 500
            log["error"] = traceback.format_exc()
            logger.error(log)
        return response
    
app = FastAPI()
app.add_middleware(LoggingMiddleware)

@app.on_event("startup")
async def startup_event():
    pass

app.include_router(api_router)