from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.core.middleware import setup_cors_middleware
from app.core.database import initialize_database
from app.api.routes import router
from app.core.config import settings
import logging

from app.data_loader import get_all_data, get_table_data, insert_dummy_data

logger = logging.getLogger(__name__)

app = FastAPI(title="ModuCar API")

setup_cors_middleware(app)

app.include_router(router)

@app.on_event("startup")
async def startup():
    """서버 시작 시 실행되는 이벤트"""
    await initialize_database()

    logger.info("🔹 더미 데이터 삽입 시작...")
    insert_dummy_data()
    logger.info("✅ 더미 데이터 삽입 완료.")

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/db", tags=["dev"])
async def get_db_data():
    return get_all_data()

@app.get("/db/{table_name}", tags=["dev"])
async def get_specific_table_data(table_name: str):
    return get_table_data(table_name)
