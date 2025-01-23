from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import router
from app.core.database import initialize_database, get_all_data, get_table_data

app = FastAPI(title="ModuCar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    initialize_database()

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """ 기본 주소(`/`)에 접속하면 `/docs`로 자동 이동 """
    return RedirectResponse(url="/docs")

@app.get("/db", tags=["dev"])
async def get_db_data():
    """ 데이터베이스의 모든 정보를 반환합니다 """
    return get_all_data()

@app.get("/db/{table}", tags=["dev"],
         summary= "특정 테이블의 정보를 반환합니다",
        description= "ex) /db/vehicle (단수형)")
async def get_table_data_endpoint(table: str):
    """ 특정 테이블의 정보를 반환합니다 """
    return get_table_data(table)