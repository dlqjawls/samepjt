from fastapi import APIRouter
from app.api.routes.user import router as user_router
from app.api.routes.admin import router as admin_router

# 메인 라우터
router = APIRouter()

router.include_router(user_router)  
router.include_router(admin_router)