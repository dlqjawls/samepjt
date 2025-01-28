from fastapi import APIRouter
from app.api.routes.user.module_set import router as module_sets_router
from app.api.routes.user.option_types import router as option_types_router
from app.api.routes.user.rent import router as rent_router

user_router = APIRouter(prefix="/user", tags=["User"])
user_router.include_router(module_sets_router)
user_router.include_router(option_types_router)
user_router.include_router(rent_router)

