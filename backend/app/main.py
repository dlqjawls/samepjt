from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import router

app = FastAPI(title="ModuCar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """ 기본 주소(`/`)에 접속하면 `/docs`로 자동 이동 """
    return RedirectResponse(url="/docs")
