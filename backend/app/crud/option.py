from sqlmodel import Session, select
from typing import List, Optional
from app.models.option import Option
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError

class OptionCRUD(CRUDBase[Option]):
    def __init__(self):
        super().__init__(Option, "option_id")
        
    def get_available_options_by_type(
        self,
        session: Session,
        option_type_id: int,
        required_quantity: int,
        status_id: int = 2  # INACTIVE
    ) -> List[Option]:
        """
        특정 옵션 타입의 사용 가능한 옵션 목록 조회

        Args:
            session: DB 세션
            option_type_id: 옵션 타입 ID
            required_quantity: 필요한 수량
            status_id: 옵션 상태 ID (기본값: INACTIVE)

        Returns:
            List[Option]: 조회된 옵션 목록

        Raises:
            DatabaseError: 데이터베이스 조회 실패 시
            NotFoundError: 필요한 수량만큼 옵션을 찾을 수 없는 경우
        """
        query = (
            select(self.model)
            .where(
                self.model.option_type_id == option_type_id,
                self.model.status_id == status_id
            )
            .limit(required_quantity)
        )

        available_options = list(session.exec(query).all())

        if len(available_options) < required_quantity:
            raise NotFoundError(
                message="Not enough options available",
                detail={
                    "option_type_id": option_type_id,
                    "required": required_quantity,
                    "available": len(available_options)
                }
            )

        return available_options
            
option_crud = OptionCRUD()