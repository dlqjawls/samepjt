from fastapi import APIRouter
from app.api.routes.admin.rent_history import router as rent_history_router
from app.api.routes.admin.vehicle import router as vehicle_router

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

admin_router.include_router(rent_history_router)
admin_router.include_router(vehicle_router)