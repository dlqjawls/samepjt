from fastapi import APIRouter
from app.api.routes.admin import login

# 관리자 라우터 모음
router = APIRouter(prefix="/admin", tags=["Admin"])

router.include_router(login.router)
