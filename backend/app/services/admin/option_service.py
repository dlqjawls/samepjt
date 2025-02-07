from typing import List
from sqlmodel import Session
from app.api.schemas.admin.option_schema import OptionDeleteResponse, OptionGetResponse, OptionItem, OptionData, OptionRegisterRequest, OptionRegisterResponse, OptionUpdateRequest, OptionUpdateResponse 
from app.db.crud.option import option_crud
from app.db.crud.option_type import option_type_crud
from app.api.schemas.common import Coordinate
from app.db.models.option import Option
from app.utils.exceptions import DatabaseError, ConflictError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from sqlalchemy import select
from app.utils.lut_constants import ItemStatus, ItemType, UsageStatus, LUTConstants
from app.db.models.usage_history import UsageHistory
import json

class OptionService:
  
    @staticmethod
    def _check_option_exists(session: Session, option_type_id: int) -> None:
        """옵션 타입 존재 여부 확인"""
        option = option_type_crud._get_by_field(session, option_type_id, "option_type_id")
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
            status=LUTConstants.ITEM_STATUS_NAMES.get(ItemStatus(option.status_id), "Unknown"),
            created_at=option.created_at,
            created_by=option.created_by,
            updated_at=option.updated_at,
            updated_by=option.updated_by
        )

    @staticmethod
    def get_option_list(session: Session, page: int, page_size: int) -> OptionGetResponse:
        "관리자 옵션 목록 조회 서비스"
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
    def register_option(session: Session, option_data: OptionRegisterRequest, user_pk: int) -> OptionRegisterResponse:
        """옵션 등록 서비스"""
        # 1. 옵션 타입 존재 여부 확인
        OptionService._check_option_exists(session, option_data.option_type_id)

        # 3. 새 옵션 생성
        new_option = Option(
            option_type_id=option_data.option_type_id,
            last_maintenance_at=datetime.now(),
            next_maintenance_at=datetime.now(),
            status_id=ItemStatus.INACTIVE,  # 초기 상태는 INACTIVE
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        option_crud.create(session, new_option)
        return OptionRegisterResponse.success(
            message="Option registered successfully"
        )

    @staticmethod
    def update_option(session: Session, option_id: int, option_data: OptionUpdateRequest, user_pk: int) -> OptionUpdateResponse:
        """
        옵션 수정 서비스 함수:
        주어진 옵션 ID에 대해 option_data를 사용해 업데이트를 수행합니다.
        """
        # 올바른 옵션 ID를 사용하여 옵션 존재 여부 확인 (수정 전: option_data를 사용하던 부분 수정)
        option = option_crud._get_by_field(session, option_id, "option_id")
        if not option:
            raise NotFoundError(
                message="Option not found",
                detail={"option_id": option_id}
            )
        
        # 업데이트할 데이터 추출 (예: 변경할 필드만 선택)
        update_data = option_data.dict(exclude_unset=True)
        
        # 옵션 업데이트 (업데이트 수행 메서드 사용, 필요시 트랜잭션 핸들러 적용)
        option_crud.update(session, option_id, update_data, id_field="option_id")
        
        return OptionUpdateResponse.success(
            message="Option updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_option(session: Session, option_id: int, user_pk: int) -> OptionDeleteResponse:
        """옵션 삭제 서비스"""
        # 옵션 존재 여부 확인
        option = option_crud._get_by_field(session, option_id, "option_id")
        if not option:
            raise NotFoundError(
                message="Option not found",
                detail={"option_id": option_id}
            )
        
        # 옵션이 현재 사용 중(대여 중)인지 UsageHistory 테이블에서 확인 (렌트 기록에는 옵션 id가 없음)
        active_usage = session.scalars(
            select(UsageHistory).where(
                UsageHistory.item_id == option_id,
                UsageHistory.item_type_id == ItemType.OPTION,
                UsageHistory.status_id == UsageStatus.IN_USE
            )
        ).first()

        if active_usage:
            raise ConflictError(
                message="Option is currently in use and cannot be deleted",
                detail={"option_id": option_id}
            )

        # 옵션 삭제
        option_crud.soft_delete(session, option_id, "option_id")

        return OptionDeleteResponse(
            resultCode="SUCCESS",
            message="Option deleted successfully"
        )   
        