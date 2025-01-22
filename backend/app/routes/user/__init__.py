from fastapi import APIRouter
from app.routes.user import login, module_sets, options, register, user_list

# 사용자 라우터 모음
router = APIRouter(prefix="/user", tags=["User"])

router.include_router(user_list.router)
router.include_router(login.router)
router.include_router(register.router)
router.include_router(module_sets.router)
router.include_router(options.router)
