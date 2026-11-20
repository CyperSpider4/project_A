import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.logging import configure_logging
from src.core.config import get_settings
    

configure_logging()

settings = get_settings()
app = FastAPI()

app.state.request_count = 0

logger = logging.getLogger("app.middleware")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def count_requests(request: Request, call_next) -> Response:
    request.app.state.request_count += 1
    
    response: Response = await call_next(request)
    
    response.headers["X-Request-Number"] = str(request.app.state.request_count)
    
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    started_at = perf_counter()
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(api_router)
