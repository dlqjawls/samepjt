from typing import Any, Dict, Optional
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
    ) -> Dict[str, Any]:
        """사용자별 렌트 기록 조회

        Args:
            session (Session): DB 세션
            user_pk (int): 사용자 PK
            page (int, optional): 페이지 번호. Defaults to 1.
            page_size (int, optional): 페이지 크기. Defaults to 10.

        Returns:
            Dict[str, Any]: 렌트 기록 및 페이지네이션 정보

        Raises:
            ValidationError: 잘못된 사용자 PK
            NotFoundError: 렌트 기록을 찾을 수 없음
            DatabaseError: DB 조회 중 오류 발생
        """
        if user_pk <= 0:
            raise ValidationError(
                message="Invalid user PK",
                detail={"user_pk": user_pk, "error": "User PK must be positive"}
            )

        query = select(self.model).where(self.model.user_pk == user_pk)
        paginated = self.paginate(session=session, page=page, page_size=page_size, query=query)

        return paginated
        
    def get_by_id(self, session: Session, rent_id: int) -> Optional[RentHistory]:
        return self._get_by_field(session, rent_id, "rent_id")

rent_history_crud = RentHistoryCRUD()