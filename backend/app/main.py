import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import initialize_database
from app.core.middleware import setup_middlewares
from app.api.routes import api_router

from app.utils.exceptions import  get_exception_handlers 
from app.websocket import websocket

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 초기화
    await initialize_database()
    yield

def create_app() -> FastAPI:
    app = FastAPI(title="ModuCar API", lifespan=lifespan, openapi_prefix="/api")

    # 전역 예외 처리
    for exc, handler in get_exception_handlers().items():
        app.add_exception_handler(exc, handler)

    # CORS
    setup_middlewares(app)
    
    # 기본 경로를 docs로 리다이렉트
    @app.get("/", include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url="/docs")

    # 라우터 등록
    app.include_router(api_router)
    
    # WebSocket 라우터 등록
    app.include_router(websocket.router)
    
    return app
