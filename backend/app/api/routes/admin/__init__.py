from fastapi import APIRouter

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# admin_router.include_router(auth_router)

