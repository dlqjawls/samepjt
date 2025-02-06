from sqlmodel import Session
from typing import List
from app.db.models.lut import ModuleType as ModuleTypeModel
from app.api.schemas.admin.module_type_schema import ModuleType as ModuleTypeSchema, ModuleTypesResponse, ModuleTypesData
from app.db.crud.lut import module_type as module_type_crud

class ModuleTypeService:
    @classmethod
    def get_all_module_types(cls, session: Session) -> ModuleTypesResponse:
        """
        DB에서 모든 모듈 타입을 CRUD 레이어(module_type_crud) 를 사용하여 조회한 후,
        ModuleTypesResponse 스키마 형식으로 반환합니다.
        """
        module_types: List[ModuleTypeModel] = module_type_crud.get_all(session)
        module_types_schema = [ModuleTypeSchema.from_orm(mt) for mt in module_types]
        return ModuleTypesResponse(
            resultCode="SUCCESS",
            message="Module types retrieved successfully",
            data=ModuleTypesData(module_types=module_types_schema)
        )