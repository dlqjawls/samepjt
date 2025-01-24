from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.core.middleware import setup_cors_middleware
from app.core.database import initialize_database
from app.api.routes import router
from app.data_loader import get_table_data, insert_dummy_data, get_all_data
from app.api.routes.test_auth import router as test_auth_router 

app = FastAPI(title="ModuCar API")

setup_cors_middleware(app)

app.include_router(router)

@app.on_event("startup")
async def startup():
    # 데이터베이스 초기화 
    initialize_database()
    # 더미 데이터 삽입
    insert_dummy_data()

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/db", tags=["dev"])
async def get_db_data():
    return get_all_data()

@app.get("/db/{table_name}", tags=["dev"])
async def get_specific_table_data(table_name: str):
    return get_table_data(table_name)


app.include_router(test_auth_router, prefix="/test")  