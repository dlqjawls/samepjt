from typing import Any, Dict
from sqlmodel import Session, select
from app.models.rent_history import RentHistory
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError
from sqlalchemy.exc import SQLAlchemyError

class RentHistoryCRUD(CRUDBase[RentHistory]):
    def __init__(self):
        super().__init__(RentHistory, "rent_id", soft_delete_field="status_id", soft_delete_value=3)
    
    def get_rents_by_user(
        self,
        session: Session,
        user_pk: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """사용자별 렌트 기록 조회

        Args:
            session: DB 세션
            user_pk: 사용자 PK
            page: 페이지 번호 (기본값: 1)
            page_size: 페이지 크기 (기본값: 10)

        Returns:
            Dict: {
                "items": List[RentHistory],
                "pagination": {
                    "current_page": int,
                    "total_pages": int,
                    "total_items": int,
                    "page_size": int
                }
            }

        Raises:
            ValidationError: 잘못된 페이지 번호/크기
            NotFoundError: 렌트 기록이 없는 경우
            DatabaseError: DB 조회 실패
        """
        try:
            # 1. 입력값 검증
            if user_pk <= 0:
                raise ValidationError(
                    message="Invalid user PK",
                    detail={
                        "user_pk": user_pk,
                        "error": "User PK must be positive"
                    }
                )

            # 2. 렌트 기록 조회
            query = (
                select(self.model)
                .where(
                    self.model.user_pk == user_pk
                )
            )
            
            # 3. 페이지네이션 적용
            paginated_result = self.paginate(session=session, page=page, page_size=page_size)

            # 4. 결과 검증
            if not paginated_result["items"]:
                raise NotFoundError(
                    message="No rent histories found",
                    detail={
                        "user_pk": user_pk,
                        "page": page,
                        "page_size": page_size
                    }
                )

            return paginated_result

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch rent histories",
                detail={
                    "error": str(e),
                    "user_pk": user_pk
                }
            )
        
    
rent_history_crud = RentHistoryCRUD()