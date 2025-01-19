from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes import user_route

app = FastAPI(title="ModuCar API")

# API 라우터 등록
app.include_router(user_route.router)

@app.get("/", include_in_schema=False)  # 🔹 Swagger 문서에서 제외
async def redirect_to_docs():
    """
    기본 주소(`/`)에 접속하면 `/docs`로 자동 이동
    """
    return RedirectResponse(url="/docs")
