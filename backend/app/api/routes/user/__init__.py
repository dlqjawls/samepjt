from fastapi import APIRouter
from app.api.routes.user import login, module_sets, option_types, register

# 사용자 라우터 모음
router = APIRouter(prefix="/user", tags=["User"])

router.include_router(login.router)
router.include_router(register.router)
router.include_router(module_sets.router)
router.include_router(option_types.router)
