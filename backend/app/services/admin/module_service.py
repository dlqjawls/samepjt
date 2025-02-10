from typing import List
from sqlmodel import Session
from app.api.schemas.admin.module_schema import ModuleDeleteResponse, ModuleItem, ModuleResponse, ModuleData, ModuleRegisterRequest, ModuleRegisterResponse, ModuleUpdateRequest, ModuleUpdateResponse 
from app.db.crud.module import module_crud
from app.api.schemas.common import Coordinate
from app.db.models.module import Module
from app.utils.exceptions import DatabaseError, ConflictError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from sqlalchemy import select
from app.utils.lut_constants import ItemStatus, ItemType, ModuleType, UsageStatus, LUTConstants
from app.db.models.usage_history import UsageHistory
import json

class ModuleService:
  
    @staticmethod
    def _check_module_exists(session: Session, module_nfc_tag_id: str) -> None:
        """모듈 NFC 태그 ID 중복 검사"""
        if module_crud.get_by_module_nfc_tag_id(session, module_nfc_tag_id):
            raise ConflictError(
                message="Module already exists",
                detail={"module_nfc_tag_id": module_nfc_tag_id, "error": "Module NFC tag ID already exists"}
            )
            
    @staticmethod
    def _convert_module_data(module: Module) -> ModuleItem:
        """모듈 데이터 변환"""
        if module.module_id is None:
            raise DatabaseError(
                message="Module ID is required",
                detail={"module": module.dict()}
            )
            
        # Retrieve module type info and extract the 'name' as a string.
        module_type_info = LUTConstants.MODULE_TYPE_INFO.get(ModuleType(module.module_type_id), {})
        module_type_name = module_type_info.get("name", "Unknown") if isinstance(module_type_info, dict) else str(module_type_info)
        
        return ModuleItem(
            module_id=module.module_id,
            module_nfc_tag_id=module.module_nfc_tag_id,
            module_type_id=module.module_type_id,
            module_type_name=module_type_name,
            last_maintenance_at=module.last_maintenance_at,
            next_maintenance_at=module.next_maintenance_at, 
            item_status_id=module.item_status_id,
            item_status_name=LUTConstants.ITEM_STATUS_NAMES.get(ItemStatus(module.item_status_id), "Unknown"),
            created_at=module.created_at,
            created_by=module.created_by,
            updated_at=module.updated_at,
            updated_by=module.updated_by
        )

    @staticmethod
    @handle_transaction
    def get_module_list(session: Session, page: int, page_size: int) -> ModuleResponse:
        "관리자 모듈 목록 조회 서비스"
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

        return ModuleResponse.success(
            data=modules_data,
            message="Module data retrieved successfully"
        )

    @staticmethod
    @handle_transaction
    def register_module(session: Session, module_data: ModuleRegisterRequest, user_pk: int) -> ModuleRegisterResponse:
        """모듈 등록 서비스"""
        # 1. NFC 태그 ID 중복 검사
        ModuleService._check_module_exists(session, module_data.module_nfc_tag_id)

        # 3. 새 모듈 생성
        new_module = Module(
            module_nfc_tag_id=module_data.module_nfc_tag_id,
            module_type_id=module_data.module_type_id,
            current_location=json.dumps(Coordinate(x=0, y=0).dict()),
            item_status_id=ItemStatus.INACTIVE,  # 초기 상태는 INACTIVE
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        module_crud.create(session, new_module)
        return ModuleResponse.success(
            message="Module registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_module(session: Session, module_id: int, module_data: ModuleUpdateRequest, user_pk: int) -> ModuleUpdateResponse:
        """
        모듈 수정 서비스 함수:
        주어진 모듈 ID에 대해 module_data를 사용해 업데이트를 수행합니다.
        """
        # 올바른 모듈 ID를 사용하여 모듈 존재 여부 확인 (수정 전: module_data를 사용하던 부분 수정)
        module = module_crud._get_by_field(session, module_id, "module_id")
        if not module:
            raise NotFoundError(
                message="Module not found",
                detail={"module_id": module_id}
            )
        
        # 업데이트할 데이터 추출 (예: 변경할 필드만 선택)
        update_data = module_data.dict(exclude_unset=True)
        print("update_data", update_data)
        
        # 모듈 업데이트 (업데이트 수행 메서드 사용, 필요시 트랜잭션 핸들러 적용)
        module_crud.update(session, module_id, update_data, id_field="module_id")
        
        return ModuleUpdateResponse.success(
            message="Module updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_module(session: Session, module_id: int, user_pk: int) -> ModuleDeleteResponse:
        """모듈 삭제 서비스"""
        # 모듈 존재 여부 확인
        module = module_crud._get_by_field(session, module_id, "module_id")
        if not module:
            raise NotFoundError(
                message="Module not found",
                detail={"module_id": module_id}
            )
        
        # 모듈이 현재 사용 중(대여 중)인지 UsageHistory 테이블에서 확인 (렌트 기록에는 모듈 id가 없음)
        active_usage = session.scalars(
            select(UsageHistory).where(
                UsageHistory.item_id == module_id,
                UsageHistory.item_type_id == ItemType.MODULE,
                UsageHistory.usage_status_id == UsageStatus.IN_USE
            )
        ).first()

        if active_usage:
            raise ConflictError(
                message="Module is currently in use and cannot be deleted",
                detail={"module_id": module_id}
            )

        # 모듈 삭제
        module_crud.soft_delete(session, module_id, "module_id")

        return ModuleDeleteResponse(
            resultCode="SUCCESS",
            message="Module deleted successfully"
        )   
        