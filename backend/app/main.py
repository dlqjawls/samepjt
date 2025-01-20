from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import RedirectResponse
from app.routes import user_route, module_set_route

app = FastAPI(title="ModuCar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)


# API 라우터 등록
app.include_router(user_route.router)
app.include_router(module_set_route.router)

@app.get("/", include_in_schema=False)  # 🔹 Swagger 문서에서 제외
async def redirect_to_docs():
    """
    기본 주소(`/`)에 접속하면 `/docs`로 자동 이동
    """
    return RedirectResponse(url="/docs")
