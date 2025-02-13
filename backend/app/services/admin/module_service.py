from typing import List
from sqlmodel import Session
from app.api.schemas.admin.module_schema import ModuleItem, ModuleGetResponse, ModuleData, ModuleRegisterRequest, ModuleMessageResponse, ModuleUpdateRequest 
from app.db.crud.module import module_crud
from app.api.schemas.common import Coordinate
from app.db.models.module import Module
from app.utils.exceptions import DatabaseError, ConflictError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from sqlalchemy import select
from app.utils.lut_constants import ItemStatus, ItemType, ModuleType, UsageStatus, MaintenanceStatus
from app.db.models.usage_history import UsageHistory
from app.db.crud.usage_history import usage_history_crud
from app.db.crud.maintenance_history import maintenance_history_crud
from app.db.crud.lut import module_type as module_type_crud
import json

class ModuleService:
  
    @staticmethod
    def _get_module_or_raise(session: Session, module_id: int) -> Module:
        """특정 모듈을 조회하고 존재하지 않으면 NotFoundError를 발생시킵니다."""
        module = module_crud.get_by_id(session, module_id)
        if not module:
            raise NotFoundError(
                message="Module not found",
                detail={"module_id": module_id}
            )
        return module
  
    @staticmethod
    def _check_module_exists(session: Session, module_nfc_tag_id: str) -> None:
        """모듈 NFC 태그 ID 중복 검사"""
        if module_crud.get_by_module_nfc_tag_id(session, module_nfc_tag_id):
            raise ConflictError(
                message="Module already exists",
                detail={"module_nfc_tag_id": module_nfc_tag_id, "error": "Module NFC tag ID already exists"}
            )
            
    @staticmethod
    def _check_module_type_exists(session: Session, module_type_id: int) -> None:
        """모듈 타입 존재 여부 확인"""
        if not module_type_crud.get_by_id(session, module_type_id):
            raise NotFoundError(
                message="Module type not found",
                detail={"module_type_id": module_type_id}
            )
    @staticmethod
    def _convert_module_data(module: Module) -> ModuleItem:
        """모듈 데이터 변환"""
        if module.module_id is None:
            raise DatabaseError(
                message="Module ID is required",
                detail={"module": module.dict()}
            )
            
        return ModuleItem(
            module_id=module.module_id,
            module_nfc_tag_id=module.module_nfc_tag_id,
            module_type_id=module.module_type_id,
            module_type_name=ModuleType.get_name(module.module_type_id),
            last_maintenance_at=module.last_maintenance_at,
            next_maintenance_at=module.next_maintenance_at, 
            item_status_id=module.item_status_id,
            item_status_name=ItemStatus.get_name(module.item_status_id),
            created_at=module.created_at,
            created_by=module.created_by,
            updated_at=module.updated_at,
            updated_by=module.updated_by
        )
        
    @staticmethod
    def _validate_module(session: Session, module_id: int) -> None:
        """모듈이 사용 중 또는 정비 중인지 확인합니다."""
        if usage_history_crud.exists_item_usage_history(
            session, module_id, ItemType.MODULE.ID, UsageStatus.IN_USE.ID
        ):
            raise ConflictError(
                message="Module is currently in use and cannot be deleted",
                detail={"module_id": module_id}
            )   
        if (
            maintenance_history_crud.exists_item_maintenance_history(
                session, module_id, ItemType.MODULE.ID, MaintenanceStatus.IN_PROGRESS.ID
            )
            or maintenance_history_crud.exists_item_maintenance_history(
                session, module_id, ItemType.MODULE.ID, MaintenanceStatus.PENDING.ID
            )
        ):
            raise ConflictError(
                message="Module is currently under maintenance and cannot be deleted",
                detail={"module_id": module_id}
            )
            
    @staticmethod
    @handle_transaction
    def get_module_list(session: Session, page: int, page_size: int) -> ModuleGetResponse:
        "관리자 모듈 목록 조회 서비스"
        
        # 모듈 목록 조회
        paginated_result = module_crud.paginate(session, page, page_size)
        modules: List[Module] = paginated_result["items"]
        
        # 모듈 데이터 변환
        module_items = [
            ModuleItem.parse_obj(
                ModuleService._convert_module_data(module)
            )
            for module in modules
        ]

        modules_data = ModuleData(
            modules=module_items,
            pagination=paginated_result["pagination"]
        )

        return ModuleGetResponse.success(
            data=modules_data,
            message="Module data retrieved successfully"
        )

    @staticmethod
    @handle_transaction
    def register_module(session: Session, module_data: ModuleRegisterRequest, user_pk: int) -> ModuleMessageResponse:
        """모듈 등록 서비스"""
        # 1. NFC 태그 ID 중복 검사
        ModuleService._check_module_exists(session, module_data.module_nfc_tag_id)
        
        # 2. 모듈 타입 존재 여부 확인
        ModuleService._check_module_type_exists(session, module_data.module_type_id)
            
        # 3. 새 모듈 생성
        new_module = Module(
            module_nfc_tag_id=module_data.module_nfc_tag_id,
            module_type_id=module_data.module_type_id,
            current_location=json.dumps(Coordinate(x=0, y=0).dict()),
            item_status_id=ItemStatus.INACTIVE.ID,  # 초기 상태는 INACTIVE
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        module_crud.create(session, new_module)
        return ModuleMessageResponse.success(
            message="Module registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_module(session: Session, module_id: int, module_data: ModuleUpdateRequest, user_pk: int) -> ModuleMessageResponse:
        """모듈 수정 서비스"""
        module = ModuleService._get_module_or_raise(session, module_id)
        ModuleService._validate_module(session, module_id)
        
        # 모듈 타입 변경 시 존재 여부 확인
        if module_data.module_type_id:
            ModuleService._check_module_type_exists(session, module_data.module_type_id)  
        
        update_data = module_data.dict(exclude_unset=True)
        update_data["updated_by"] = user_pk
        update_data["updated_at"] = datetime.now()
        
        module_crud.update(session, module_id, update_data, "module_id")
        
        return ModuleMessageResponse.success(
            message="Module updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_module(session: Session, module_id: int, user_pk: int) -> ModuleMessageResponse:
        """모듈 삭제 서비스"""
        module = ModuleService._get_module_or_raise(session, module_id)
        ModuleService._validate_module(session, module_id)
        
        module_crud.soft_delete(session, module_id, "module_id")

        return ModuleMessageResponse.success(
            message="Module deleted successfully"
        )   
        