from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.admin import admin_router
from app.api.routes.user import user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(user_router)

