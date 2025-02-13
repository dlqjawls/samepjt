from typing import Any, Dict, Optional, List
from sqlmodel import Session, select
from app.db.models.rent_history import RentHistory
from app.db.crud.base import CRUDBase
from app.utils.exceptions import ValidationError

class RentHistoryCRUD(CRUDBase[RentHistory]):
    def __init__(self):
        super().__init__(RentHistory)
    
    def get_rents_by_user(
        self,
        session: Session,
        user_pk: int,
        page: int = 1,
        page_size: int = 10
    ) -> List[RentHistory]:
        """사용자별 렌트 기록 조회"""
        if user_pk <= 0:
            raise ValidationError(
                message="Invalid user PK",
                detail={"user_pk": user_pk, "error": "User PK must be positive"}
            )

        query = select(self.model).where(self.model.user_pk == user_pk)
        return list(session.exec(query).all())
        
    def get_by_id(self, session: Session, rent_id: int) -> Optional[RentHistory]:
        return self.get_by_field(session, rent_id, "rent_id")

rent_history_crud = RentHistoryCRUD()