from sqlmodel import Session, select, update
from app.models.vehicle import Vehicle
from app.models.module import Module
from app.models.option import Option
from app.models.usage_history import UsageHistory
from app.crud.base import CRUDBase
from sqlalchemy.exc import IntegrityError
from typing import List

from app.utils.exceptions import DatabaseError

class UsageHistoryCRUD(CRUDBase[UsageHistory]):
    def __init__(self):
        super().__init__(UsageHistory, "usage_id")
        
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
      
    def cancel_usage_entries(
        self,
        session: Session,
        rent_id: int,
        vehicle_id: int,
        module_id:int,
        option_ids: List[int]
    ) -> None:
        """사용 기록 및 아이템 상태 업데이트"""
        # 사용 기록 상태 업데이트
        session.execute(
            update(UsageHistory)
            .where(UsageHistory.rent_id == rent_id)
            .values(status_id=2)  # INACTIVE
        )

        # 차량 상태 업데이트
        if vehicle_id:
            session.execute(
                update(Vehicle)
                .where(Vehicle.vehicle_id == vehicle_id)
                .values(status_id=2)  # INACTIVE
            )

        # 모듈 상태 업데이트
        if module_id:
            session.execute(
                update(Module)
                .where(Module.module_id == module_id)
                .values(status_id=2)  # INACTIVE
            )

        # 옵션 상태 업데이트
        if option_ids:
            session.execute(
                update(Option)
                .where(Option.option_id.in_(option_ids))
                .values(status_id=2)  # INACTIVE
            )

    def bulk_create(self, session: Session, usage_entries: List[UsageHistory]) -> List[UsageHistory]:
        """ UsageHistory 여러 개 한 번에 저장 """
        try:
            session.add_all(usage_entries)
            session.flush() 
            return usage_entries
        except IntegrityError as e:
            raise DatabaseError(
                message="Failed to create usage histories",
                detail={"error": str(e)}
            )


    def soft_delete(self, session: Session, rent_id: int):
        """특정 rent_id에 해당하는 모든 usage history의 상태를 변경"""
        try:
            # 존재 여부 확인
            usage_entries = session.exec(
                select(UsageHistory).where(UsageHistory.rent_id == rent_id)
            ).all()

            if not usage_entries:
                return 

            # 상태 일괄 업데이트
            stmt = update(UsageHistory).where(
                UsageHistory.rent_id == rent_id
            ).values(status_id=2)  # INACTIVE 상태
            session.execute(stmt)
            
            session.flush()
            
        except Exception as e:
            raise DatabaseError(
                message="Failed to soft delete usage histories",
                detail={
                    "error": str(e),
                    "rent_id": rent_id
                }
            )
            
usage_history_crud = UsageHistoryCRUD()
