from sqlmodel import Session
from app.db.models.maintenance_history import MaintenanceHistory  # 해당 모델이 존재한다고 가정
from datetime import datetime
from app.utils.exceptions import NotFoundError, ConflictError   
from app.db.models.vehicle import Vehicle
from app.db.models.module import Module
from app.db.models.option import Option
from app.api.schemas.admin.maintenance_history_schema import (
    MaintenanceHistoryGetResponse,
    MaintenanceHistoryData,
    MaintenanceHistoryItem,
    MaintenanceHistoryPostRequest,
    MaintenanceHistoryPostResponse,
    MaintenanceHistoryPatchRequest,
    MaintenanceHistoryPatchResponse,
    MaintenanceHistoryDeleteResponse
)
from typing import Optional, Union, List, cast
from app.utils.lut_constants import MaintenanceStatus, ItemStatus, ItemType
from app.utils.handle_transaction import handle_transaction
from app.db.crud.lut import item_type
from app.db.crud.maintenance_history import maintenance_history_crud
from app.db.crud.lut import maintenance_status

class MaintenanceHistoryService:
  
    @staticmethod
    def _fetch_item(session: Session, item_type_id: int, item_id: int) -> Optional[Union[Vehicle, Module, Option]]:
        """주어진 item_type_id, item_id에 해당하는 아이템을 조회합니다."""
        mapping = {"vehicle": Vehicle, "module": Module, "option": Option}
        model = mapping.get(ItemType.get_name(item_type_id))
        return cast(Optional[Union[Vehicle, Module, Option]], session.get(model, item_id))
      
    @staticmethod
    def _update_item_status(session: Session, item: Union[Vehicle, Module, Option], item_status_id: int):
        """아이템 상태를 업데이트합니다."""
        item.item_status_id = item_status_id
        item.last_maintenance_at = datetime.now()
        item.next_maintenance_at = None

    @staticmethod
    @handle_transaction
    def get_maintenance_history(
        session: Session,
        page: int = 1,
        pageSize: int = 10,
        itemType: Optional[str] = None,
        itemId: Optional[int] = None,
    ) -> MaintenanceHistoryGetResponse:
        """정비 기록 목록을 조회합니다."""
        
        query = maintenance_history_crud.get_list(session, page=page, page_size=pageSize)
        pagination = query["pagination"]
        histories = query["items"]
        
        
        maintenance_items :List[MaintenanceHistoryItem] = [
          MaintenanceHistoryItem(
            maintenance_id = cast(int, history.maintenance_id),
            item_type_name = ItemType.get_name(history.item_type_id),
            item_id = history.item_id,
            issue = history.issue,
            cost = history.cost,
            maintenance_status_name = MaintenanceStatus.get_name(history.maintenance_status_id),
            scheduled_at = history.scheduled_at,
            completed_at = history.completed_at,
            created_at = history.created_at,
            created_by = history.created_by,
            updated_at = history.updated_at,
            updated_by = history.updated_by
          )
          for history in histories
        ]
        
        
        return MaintenanceHistoryGetResponse.success(
            message="Maintenance history retrieved successfully",
            data=MaintenanceHistoryData(
                maintenance_history=maintenance_items,
                pagination=pagination
            )
        )

    @staticmethod
    @handle_transaction
    def create_maintenance_history(
        session: Session,
        payload: MaintenanceHistoryPostRequest,
        user_pk: int
    ) -> MaintenanceHistoryPostResponse:
        """새로운 정비 기록을 생성합니다."""
        item = maintenance_history_crud.fetch_item(session, ItemType.get_id(payload.item_type_name), payload.item_id)
        if item is None:
            raise NotFoundError(
                message="Item not found",
                detail={"item_id": payload.item_id, "item_type_name": payload.item_type_name}
            )
            
        # 아이템이 사용 중 또는 정비 중이면 정비 기록 생성 불가
        if item.item_status_id in (ItemStatus.ACTIVE.ID, ItemStatus.MAINTENANCE.ID):
            raise ConflictError(
                message="Item is not inactive",
                detail={"item_id": payload.item_id, "item_type_name": payload.item_type_name}
            )

        # 새 정비 기록 생성 (정비 상태는 기본값 pending => 1)
        new_history = MaintenanceHistory(
            item_type_id = ItemType.get_id(payload.item_type_name),
            item_id=payload.item_id,
            issue=payload.issue,
            cost=payload.cost,
            maintenance_status_id=MaintenanceStatus.PENDING.ID,
            scheduled_at=payload.scheduled_at if payload.scheduled_at else datetime.now(),
            completed_at=payload.completed_at,
            created_at=datetime.now(),
            created_by=user_pk,
            updated_at=datetime.now(),
            updated_by=user_pk
        )
        
        maintenance_history_crud.create(session, new_history) 
        
        return MaintenanceHistoryPostResponse.success(
            message="Maintenance history created successfully"
        )

    @staticmethod
    @handle_transaction
    def update_maintenance_history(
        session: Session,
        maintenance_id: int,
        payload: MaintenanceHistoryPatchRequest,
        user_pk: int
    ) -> MaintenanceHistoryPatchResponse:
        """정비 기록 정보를 수정합니다."""       
        history = maintenance_history_crud.get_by_id(session, maintenance_id)
        if not history:
            raise NotFoundError(
                message="Maintenance history not found",
                detail={"maintenance_id": maintenance_id}
            )
            
        # 완료된 정비 기록은 수정할 수 없음 
        if history.maintenance_status_id == MaintenanceStatus.COMPLETED.ID:
            raise ConflictError(
                message="Cannot modify a completed maintenance history",
                detail={"maintenance_id": maintenance_id, "status": "completed"}
            )
        
        # 아이템 존재 여부 검증 
        item = maintenance_history_crud.fetch_item(session, history.item_type_id, history.item_id)

        if not item:
            raise NotFoundError(
                message="Item not found",
                detail={"item_id": history.item_id, "item_type": history.item_type_id}
            )
            
        update_data = payload.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        update_data["updated_by"] = user_pk 
        
        maintenance_history_crud.update(session, maintenance_id, update_data, "maintenance_id")
        
        # 정비 완료 시 아이템 상태 업데이트   
        if update_data.get("maintenance_status_id") == MaintenanceStatus.COMPLETED.ID:
            item.item_status_id = ItemStatus.INACTIVE.ID
            item.last_maintenance_at = history.completed_at
            item.next_maintenance_at = None
            session.add(item)
            session.flush()
            session.refresh(item)
            
        return MaintenanceHistoryPatchResponse.success(
            message="Maintenance history updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_maintenance_history(
        session: Session,
        maintenance_id: int,
        user_pk: int
    ) -> MaintenanceHistoryDeleteResponse:
        """        정비 기록을 삭제(소프트 삭제)하는 서비스 로직입니다.        """
        
        history = session.get(MaintenanceHistory, maintenance_id)
        if not history:
            raise NotFoundError(
                message="Maintenance history not found",
                detail={"maintenance_id": maintenance_id}
            )

        # 정비 기록이 진행 중이면 삭제할 수 없음
        if history.maintenance_status_id == 2:
            raise ConflictError(
                message="Cannot delete a in progress maintenance history",
                detail={"maintenance_id": maintenance_id, "status": "in progress"}
            )
            
        # 정비 기록 삭제
        maintenance_history_crud.soft_delete(session, maintenance_id, "maintenance_id")
        
        # 정비 기록 삭제 시 아이템 상태 업데이트
        item = MaintenanceHistoryService._fetch_item(session, history.item_type_id, history.item_id)
        if item:
            item.item_status_id = 2
            session.add(item)
            session.flush()
            session.refresh(item) 

        return MaintenanceHistoryDeleteResponse.success(
            message="Maintenance history deleted successfully"
        ) 