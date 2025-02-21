from sqlmodel import Session, select
from sqlalchemy import func
from app.db.models.maintenance_history import MaintenanceHistory  # 해당 모델이 존재한다고 가정
from app.api.schemas.common import Pagination
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
from app.utils.lut_constants import ItemStatus
from app.utils.handle_transaction import handle_transaction
from app.db.crud.lut import item_type
from app.db.crud.maintenance_history import maintenance_history_crud
from app.db.crud.lut import maintenance_status

class MaintenanceHistoryService:
  
    @staticmethod
    def _fetch_item(session: Session, item_type_value, item_id: int) -> Optional[Union[Vehicle, Module, Option]]:
        """
        아이템 조회를 위한 공통 함수.
        만약 item_type_value가 문자열이면 payload에서 사용되는 값(예: "vehicle", "module", "option")으로 간주하고,
        정수라면 MaintenanceHistory에 저장된 item_type_id로 LUT 조회 후, 해당 아이템의 타입 이름을 구합니다.
        이후, 아이템 타입에 해당하는 모델(Vehicle, Module, Option)을 이용해 아이템을 조회합니다.
        """
        if isinstance(item_type_value, str):
            type_name = item_type_value.lower()
        else:
            lut = item_type.get_by_id(session, item_type_value)
            type_name = lut.item_type_name.lower() 
        mapping = {"vehicle": Vehicle, "module": Module, "option": Option}
        model = mapping.get(type_name)
        if model is None:
            raise ValueError(f"Invalid item type: {type_name}")
        return cast(Optional[Union[Vehicle, Module, Option]], session.get(model, item_id))

    @staticmethod
    @handle_transaction
    def get_maintenance_history(
        session: Session,
        page: int = 1,
        pageSize: int = 10,
        itemType: Optional[str] = None,
        itemId: Optional[int] = None,
    ) -> MaintenanceHistoryGetResponse:
        """
        지정된 조건에 따라 정비 기록을 조회하는 서비스 로직입니다.
        
        Args:
            session (Session): 데이터베이스 세션.
            page (int): 현재 페이지 (기본값: 1).
            pageSize (int): 한 페이지당 정비 기록 수 (기본값: 10).
            itemType (Optional[int]): 정비 대상의 타입 ID. (예: 차량, 모듈, 옵션 등)
            itemId (Optional[int]): 특정 아이템의 고유 ID. itemType이 제공된 경우에만 사용.
        
        Raises:
            ConflictError: 아이템 타입이 제공되지 않은 상태에서 아이템 아이디가 지정된 경우.
        
        Returns:
            MaintenanceHistoryGetResponse: 정비 기록 조회 응답 스키마.
        """
        # deleted_at이 없는 정비 기록만 조회
        filters = [MaintenanceHistory.deleted_at == None]
        
        # 아이템 타입이 없으면 아이템 아이디를 사용할 수 없음
        if itemId is not None and itemType is None:
            raise ConflictError("아이템 타입이 지정되지 않은 상태에서 아이템 아이디를 사용할 수 없습니다.")
        
        # 동적으로 필터를 구성
        if itemType is not None:
            filters.append(MaintenanceHistory.item_type_id == item_type.get_by_name(session, itemType).item_type_id)
        if itemId is not None:
            filters.append(MaintenanceHistory.item_id == itemId)
        
        stmt = select(MaintenanceHistory)
        if filters:
            stmt = stmt.where(*filters)
        
        total_query = select(func.count()).select_from(MaintenanceHistory)
        if filters:
            total_query = total_query.where(*filters)
        total_items = session.exec(total_query).one()
        
        histories = session.exec(stmt.offset((page - 1) * pageSize).limit(pageSize)).all()

        maintenance_items :List[MaintenanceHistoryItem] = [
          MaintenanceHistoryItem(
            maintenance_id = cast(int, history.maintenance_id),
            item_type_name = item_type.get_by_id(session, history.item_type_id).item_type_name,
            item_id = history.item_id,
            issue = history.issue,
            cost = history.cost,
            maintenance_status_name = maintenance_status.get_by_id(session, history.maintenance_status_id).maintenance_status_name,
            scheduled_at = history.scheduled_at,
            completed_at = history.completed_at,
            created_at = history.created_at,
            created_by = history.created_by,
            updated_at = history.updated_at,
            updated_by = history.updated_by
          )
          for history in histories
        ]
        total_pages = (total_items + pageSize - 1) // pageSize if total_items else 0
        
        pagination = Pagination(
            currentPage=page,
            totalPages=total_pages,
            totalItems=total_items,
            pageSize=pageSize
        )
        
        data = MaintenanceHistoryData(
            maintenance_history=maintenance_items,
            pagination=pagination
        )
        
        return MaintenanceHistoryGetResponse.success(
            message="Maintenance history retrieved successfully",
            data=data
        )

    @staticmethod
    @handle_transaction
    def create_maintenance_history(
        session: Session,
        payload: MaintenanceHistoryPostRequest,
        user_pk: int
    ) -> MaintenanceHistoryPostResponse:
        """
        새로운 정비 기록을 생성하는 서비스 로직입니다.
        
        Args:
            session (Session): 데이터베이스 세션.
            payload (MaintenanceHistoryPostRequest): 정비 기록 생성 요청 데이터.
            user_pk (int): 정비 기록을 등록한 사용자 ID.
        
        Returns:
            MaintenanceHistoryPostResponse: 정비 기록 등록 결과 응답 스키마.
        """
        # 아이템 존재 여부 검증 (중복 코드 제거: _fetch_item 사용)
        item = MaintenanceHistoryService._fetch_item(session, payload.item_type_name, payload.item_id)

        if not item:
            raise NotFoundError(
                message="Item not found",
                detail={"item_id": payload.item_id, "item_type_name": payload.item_type_name}
            )
            
        # 아이템이 사용 중 또는 정비 중이면 정비 기록 생성 불가
        if item.item_status_id in (1, 3):  # 1: 사용 중, 3: 정비 중
            raise ConflictError(
                message="Item is not inactive",
                detail={"item_id": payload.item_id, "item_type_name": payload.item_type_name}
            )

        # 새 정비 기록 생성 (정비 상태는 기본값 pending => 1)
        new_history = MaintenanceHistory(
            item_type_id = item_type.get_by_name(session, payload.item_type_name).item_type_id,
            item_id=payload.item_id,
            issue=payload.issue,
            cost=payload.cost,
            maintenance_status_id=1,  # 정비 상태 'pending'
            scheduled_at=payload.scheduled_at if payload.scheduled_at else datetime.now(),
            completed_at=payload.completed_at,
            created_at=datetime.now(),
            created_by=user_pk,
            updated_at=datetime.now(),
            updated_by=user_pk
        )
        
        session.add(new_history)
        session.flush()  # 새 레코드를 flush하여 persistent 상태로 만듦
        session.refresh(new_history)
        
        # 아이템의 상태 및 정비 날짜 업데이트
        if payload.item_type_name in ("vehicle", "module", "option"):
            item.item_status_id = 3  # 예를 들어, '정비 중' 상태
            item.next_maintenance_at = payload.scheduled_at

        session.add(item)
        session.flush()  # 아이템도 flush하여 persistent 상태로 만듦
        session.refresh(item)
        
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
        """
        정비 기록 정보를 수정하는 서비스 로직입니다.
        
        Args:
            session (Session): 데이터베이스 세션.
            maintenance_id (int): 수정할 정비 기록의 ID.
            payload (MaintenanceHistoryPatchRequest): 수정 요청 데이터.
            user_pk (int): 수정 요청을 수행한 사용자 ID.
        
        Returns:
            MaintenanceHistoryPatchResponse: 수정 결과 응답 스키마.
        """       
               
        # 정비 기록 존재 여부 확인
        history = session.get(MaintenanceHistory, maintenance_id)
        if not history:
            raise NotFoundError(
                message="Maintenance history not found",
                detail={"maintenance_id": maintenance_id}
            )
            
        # 완료된 정비 기록은 수정할 수 없음 (예: status_id == 3)
        if history.maintenance_status_id == 3:
            raise ConflictError(
                message="Cannot modify a completed maintenance history",
                detail={"maintenance_id": maintenance_id, "status": "completed"}
            )
        
        # 아이템 존재 여부 검증 (중복 코드 제거: _fetch_item 사용)
        item = MaintenanceHistoryService._fetch_item(session, history.item_type_id, history.item_id)

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
        if update_data.get("maintenance_status_id") == 3:
            item.item_status_id = 2
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
        """
        정비 기록을 삭제(소프트 삭제)하는 서비스 로직입니다.
        
        Args:
            session (Session): 데이터베이스 세션.
            maintenance_id (int): 삭제할 정비 기록의 ID.
            user_pk (int): 삭제 요청을 수행한 사용자 ID.
        
        Returns:
            MaintenanceHistoryDeleteResponse: 삭제 결과 응답 스키마.
        """
        
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