from sqlmodel import Session
from app.db.crud.usage_history import usage_history_crud
from app.utils.lut_constants import ItemType, UsageStatus
from app.api.schemas.admin.usage_history_schema import (
    UsageHistoryGetResponse,
    UsageHistoryData,
    UsageHistoryItem,
)


class UsageHistoryService:
  
    @staticmethod
    def get_usage_history(session: Session, page: int, page_size: int) -> UsageHistoryGetResponse:
        """사용 이력 데이터를 조회합니다."""

        query_result = usage_history_crud.get_list(session, page=page, page_size=page_size, include_deleted=True)
        history_list = query_result["items"]
        pagination = query_result["pagination"]
        
        # DB 레코드를 스키마 항목으로 매핑
        usage_history_items = [
            UsageHistoryItem(
                usage_id=history.usage_id,
                rent_id=history.rent_id,
                item_id=history.item_id,
                item_type_name=ItemType.get_name(history.item_type_id),
                usage_status_name=UsageStatus.get_name(history.usage_status_id),
                created_at=history.created_at,
                updated_at=history.updated_at
            )
            for history in history_list
        ]

       
        return UsageHistoryGetResponse(
            resultCode="SUCCESS",
            message="Usage history retrieved successfully",
            data=UsageHistoryData(
                usage_history=usage_history_items,
                pagination=pagination
            )
        ) 