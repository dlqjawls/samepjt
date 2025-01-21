from fastapi import APIRouter
from app.routes.user import router as user_router

# 메인 라우터
router = APIRouter()

router.include_router(user_router)  