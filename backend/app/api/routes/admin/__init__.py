from fastapi import APIRouter
from app.api.routes.admin.rent_history import router as rent_history_router
from app.api.routes.admin.vehicle import router as vehicle_router
from app.api.routes.admin.module import router as module_router
from app.api.routes.admin.module_type import router as module_type_router
from app.api.routes.admin.option import router as option_router
from app.api.routes.admin.module_set import router as module_set_router
from app.api.routes.admin.option_type import router as option_type_router
from app.api.routes.admin.usage_history import router as usage_history_router
from app.api.routes.admin.maintenance_status import router as maintenance_status_router
from app.api.routes.admin.maintenance_history import router as maintenance_history_router
from app.api.routes.admin.dashboard import router as dashboard_router

admin_router = APIRouter(prefix="/admin", tags=["Admin"])   

admin_router.include_router(vehicle_router)
admin_router.include_router(module_router)
admin_router.include_router(option_router)
admin_router.include_router(module_set_router)
admin_router.include_router(option_type_router)
admin_router.include_router(rent_history_router)
admin_router.include_router(usage_history_router)
admin_router.include_router(maintenance_history_router)
admin_router.include_router(maintenance_status_router)
admin_router.include_router(module_type_router)
admin_router.include_router(dashboard_router)