from typing import Any, Dict, Optional, List
from sqlmodel import Session, select
from app.db.models.rent_history import RentHistory
from app.db.crud.base import CRUDBase

class RentHistoryCRUD(CRUDBase[RentHistory]):
    def __init__(self):
        super().__init__(RentHistory)
    
    def get_rents_by_user(
        self,
        session: Session,
        user_pk: int,
        rent_status_id: Optional[int] = None
    ) -> List[RentHistory]:
        """사용자별 렌트 기록 조회"""
        query = select(self.model).where(
            self.model.user_pk == user_pk,
            self.model.rent_status_id == rent_status_id if rent_status_id else True
        )
        return list(session.exec(query).all())
        
    def get_by_id(self, session: Session, rent_id: int) -> Optional[RentHistory]:
        return self.get_by_field(session, rent_id, "rent_id")

rent_history_crud = RentHistoryCRUD()