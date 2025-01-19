from fastapi import FastAPI
from app.routes import user_route

app = FastAPI(title="ModuCar API")

# API 라우터 등록
app.include_router(user_route.router)

@app.get("/")
async def root():
    return {"message": "ModuCar FastAPI 서버 실행 중"}
