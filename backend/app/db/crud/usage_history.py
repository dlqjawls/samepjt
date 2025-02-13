from sqlmodel import Session, select, update
from app.db.models.usage_history import UsageHistory
from app.db.crud.base import CRUDBase
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, List, Optional
from app.utils.lut_constants import ItemType, UsageStatus
from app.utils.exceptions import DatabaseError, ValidationError

class UsageHistoryCRUD(CRUDBase[UsageHistory]):
    def __init__(self):
        super().__init__(UsageHistory)
          
    
    def _update_status(
        self,
        session: Session,
        model,
        identifier: int,
        field_name: str,
        usage_status_id: int,
        extra_conditions: Optional[List[Any]] = None

    ) -> None:
        """지정된 모델의 특정 필드를 기준으로 상태 업데이트를 수행하는 헬퍼 메서드입니다.
        추가 조건이 있다면 rent id 등도 함께 필터링합니다. """


        condition = getattr(model, field_name) == identifier
        if extra_conditions:
            for cond in extra_conditions:
                condition = condition & cond
        session.execute(
            update(model)
            .where(condition)
            .values(usage_status_id=usage_status_id)
        )
        

        
    def get_item_usage_history(
        self,
        session: Session,
        item_id: int,
        item_type_id: int
    ) -> List[UsageHistory]:
        """특정 아이템의 사용 기록 조회"""
        
        # 입력값 검증
        if item_id <= 0:
            raise ValidationError(
                message="Invalid item ID",
                detail={
                    "item_id": item_id,
                    "error": "Item ID must be positive"
                }
            )

        # 사용 기록 조회
        query = (
            select(self.model)
            .where(
                self.model.item_id == item_id,
                self.model.item_type_id == item_type_id
            )
        )

        return list(session.exec(query).all())
      
    def get_usage_entries(
        self,
        session: Session,
        rent_id: int
    ) -> List[UsageHistory]:
        """렌트의 사용 기록 조회"""

        usage_entries = session.exec(
            select(UsageHistory)
            .where(UsageHistory.rent_id == rent_id)
        ).all()

        return list(usage_entries)

    def create_usage_entries(
        self,
        session: Session,
        rent_id: int,
        vehicle_id: int,
        module_id: int,
        option_ids: List[int]
    ) -> List[UsageHistory]:
        """렌트에 대한 사용 기록 생성"""
        try:
            # 입력값 검증
            if rent_id <= 0:
                raise ValidationError(
                    message="Invalid rent ID",
                    detail={"rent_id": rent_id}
                )
            if vehicle_id <= 0:
                raise ValidationError(
                    message="Invalid vehicle ID",
                    detail={"vehicle_id": vehicle_id}
                )
            if module_id <= 0:
                raise ValidationError(
                    message="Invalid module ID",
                    detail={"module_id": module_id}
                )
            if any(opt_id <= 0 for opt_id in option_ids):
                raise ValidationError(
                    message="Invalid option ID",
                    detail={"option_ids": option_ids}
                )

            # 사용 기록 생성
            items = [(ItemType.VEHICLE.ID, vehicle_id), (ItemType.MODULE.ID, module_id)] + [(ItemType.OPTION.ID, oid) for oid in option_ids]
            usage_entries = [
                UsageHistory(rent_id=rent_id, item_id=item, item_type_id=item_type, usage_status_id=UsageStatus.IN_USE.ID)
                for item_type, item in items if item > 0
            ]


            # DB에 일괄 저장
            session.add_all(usage_entries)
            session.flush()

            return usage_entries

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to create usage entries",
                detail={
                    "error": str(e),
                    "rent_id": rent_id
                }
            )


    def update_usage_entries_status(
        self,
        session: Session,
        rent_id: int,
        vehicle_id: Optional[int],
        module_id: Optional[int],
        option_ids: List[int],
        usage_status_id: int
    ) -> None:
        """사용 기록 업데이트"""
        try:
            # 업데이트 대상 및 항목 타입 매핑
            updates = []
            if vehicle_id is not None:
                updates.append((ItemType.VEHICLE.ID, vehicle_id))
            if module_id is not None:
                updates.append((ItemType.MODULE.ID, module_id))
            if option_ids:
                for oid in option_ids:
                    updates.append((ItemType.OPTION.ID, oid))

            for item_type, item_id in updates:
                self._update_status(
                    session,
                    UsageHistory,
                    item_id,
                    "item_id",
                    usage_status_id,
                    extra_conditions=[UsageHistory.item_type_id == item_type, UsageHistory.rent_id == rent_id]

                )
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to update usage entries status",
                detail={
                    "error": str(e),
                    "rent_id": rent_id,
                    "usage_status_id": usage_status_id
                }
            )

    def exists_item_usage_history(
        self, session: Session, item_id: int, item_type: int, usage_status: int
    ) -> bool:
        """주어진 item_id, item_type, usage_status에 해당하는 사용 이력 레코드가 존재하는지 확인합니다."""
        query = select(self.model).where(
            self.model.item_id == item_id,
            self.model.item_type_id == item_type,
            self.model.usage_status_id == usage_status
        )
        result = session.exec(query).first()
        return result is not None

usage_history_crud = UsageHistoryCRUD()
