from typing import List
from sqlmodel import Session
from app.api.schemas.admin.option_schema import OptionMessageResponse, OptionGetResponse, OptionItem, OptionData, OptionRegisterRequest, OptionUpdateRequest 
from app.db.crud.option import option_crud
from app.db.crud.option_type import option_type_crud
from app.db.crud.usage_history import usage_history_crud
from app.db.crud.maintenance_history import maintenance_history_crud
from app.db.models.option import Option
from app.utils.exceptions import DatabaseError, ConflictError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from sqlalchemy import select
from app.utils.lut_constants import ItemStatus, ItemType, UsageStatus, MaintenanceStatus
from app.db.models.usage_history import UsageHistory
import json

class OptionService:
  
    @staticmethod 
    def _get_option_or_raise(session: Session, option_id: int) -> Option:
        """특정 옵션을 조회하고 존재하지 않으면 NotFoundError를 발생시킵니다."""
        option = option_crud.get_by_id(session, option_id)
        if not option:
            raise NotFoundError(
                message="Option not found",
                detail={"option_id": option_id}
            )
        return option
    
    @staticmethod
    def _check_option_type_exists(session: Session, option_type_id: int) -> None:
        """옵션 타입 존재 여부 확인"""
        option = option_type_crud.get_by_id(session, option_type_id)
        if option is None:
            raise NotFoundError(
                message="Option type not found",
                detail={"option_type_id": option_type_id}
            )
            
    @staticmethod
    def _convert_option_data(option: Option) -> OptionItem:
        """옵션 데이터 변환"""
        if option.option_id is None:
            raise DatabaseError(
                message="Option ID is required",
                detail={"option": option.dict()}
            )
            
        return OptionItem(
            option_id=option.option_id,
            option_type_id=option.option_type_id,
            last_maintenance_at=option.last_maintenance_at,
            next_maintenance_at=option.next_maintenance_at, 
            item_status_name=ItemStatus.get_name(option.item_status_id),
            created_at=option.created_at,
            created_by=option.created_by,
            updated_at=option.updated_at,
            updated_by=option.updated_by
        )
        
    @staticmethod
    def _validate_option(session: Session, option_id: int) -> None:
        """옵션이 사용 중 또는 정비 중인지 확인합니다."""
        if usage_history_crud.exists_item_usage_history(
            session, option_id, ItemType.OPTION.ID, UsageStatus.IN_USE.ID
        ):
            raise ConflictError(
                message="Option is currently in use and cannot be deleted",
                detail={"option_id": option_id}
            )   
        if (
            maintenance_history_crud.exists_item_maintenance_history( 
                session, option_id, ItemType.OPTION.ID, MaintenanceStatus.IN_PROGRESS.ID
            )
            or maintenance_history_crud.exists_item_maintenance_history(
                session, option_id, ItemType.OPTION.ID, MaintenanceStatus.PENDING.ID
            )
        ):
            raise ConflictError(
                message="Option is currently in use and cannot be deleted",
                detail={"option_id": option_id}
            )
            
    @staticmethod
    def get_option_list(session: Session, page: int, page_size: int) -> OptionGetResponse:
        """옵션 목록 조회 서비스"""
                
        # 옵션 목록 조회
        paginated_result = option_crud.paginate(session, page, page_size)
        options: List[Option] = paginated_result["items"]
        
        # 옵션 데이터 변환
        option_items = [
            OptionItem.parse_obj(
                OptionService._convert_option_data(option)
            )
            for option in options
        ]

        options_data = OptionData(
            options=option_items,
            pagination=paginated_result["pagination"]
        )

        return OptionGetResponse.success(
            data=options_data,
            message="Option data retrieved successfully"
        )

    @staticmethod
    @handle_transaction
    def register_option(session: Session, option_data: OptionRegisterRequest, user_pk: int) -> OptionMessageResponse:
        """옵션 등록 서비스"""
        # 옵션 타입 존재 여부 확인
        OptionService._check_option_type_exists(session, option_data.option_type_id)

        # 새 옵션 생성
        new_option = Option(
            option_type_id=option_data.option_type_id,
            last_maintenance_at=datetime.now(),
            next_maintenance_at=datetime.now(),
            item_status_id=ItemStatus.INACTIVE.ID,  # 초기 상태는 INACTIVE
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        option_crud.create(session, new_option)
        return OptionMessageResponse.success(
            message="Option registered successfully"
        )

    # NOTE: 미사용 (변경할 항목이 없음)
    @staticmethod
    @handle_transaction
    def update_option(session: Session, option_id: int, option_data: OptionUpdateRequest, user_pk: int) -> OptionMessageResponse:
        """옵션 수정 서비스"""
        option = OptionService._get_option_or_raise(session, option_id)
        OptionService._validate_option(session, option_id)
        
        # 옵션 타입 변경 시 존재 여부 확인
        if option_data.option_type_id:
            OptionService._check_option_type_exists(session, option_data.option_type_id)
        
        update_data = option_data.dict(exclude_unset=True)
        update_data["updated_by"] = user_pk
        update_data["updated_at"] = datetime.now()
        
        option_crud.update(session, option_id, update_data, id_field="option_id")
        
        return OptionMessageResponse.success(
            message="Option updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_option(session: Session, option_id: int, user_pk: int) -> OptionMessageResponse:
        """옵션 삭제 서비스"""
        option = OptionService._get_option_or_raise(session, option_id)
        OptionService._validate_option(session, option_id)
        
        option_crud.soft_delete(session, option_id, "option_id")

        return OptionMessageResponse.success(
            message="Option deleted successfully"
        )