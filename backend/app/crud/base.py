from typing import Dict, Optional, TypeVar, Type, Generic, List, Any
from sqlmodel import SQLModel, Session, select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException

from app.utils.exceptions import DatabaseError, NotFoundError




T = TypeVar("T", bound=SQLModel)

class CRUDBase(Generic[T]):
    def __init__(
        self,
        model: Type[T],
        id_field: Optional[str] = None,
        soft_delete_field: Optional[str] = None,
        soft_delete_value: Any = None,
    ):
        """
        :param model: SQLModel 모델 클래스
        :param id_field: get_by_id()에서 사용할 기본 ID 필드명 (예: 'user_id')
        :param soft_delete_field: 소프트 삭제용 필드명 (예: 'deleted_at', 'is_deleted')
        :param soft_delete_value: 소프트 삭제 시 세팅할 값 (예: True, datetime.now(), 4(id))
        """
        self.model = model
        self.id_field = id_field
        self.soft_delete_field = soft_delete_field
        self.soft_delete_value = soft_delete_value

    def create(self, session: Session, obj_in) -> T:
        """
        객체 생성
        flush()로 DB에 반영
        """
        try:
            db_obj = self.model(**obj_in.dict())
            session.add(db_obj)
            session.flush()
            session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            session.rollback()
            raise DatabaseError(
                message="Database integrity error during create()",
                detail={"origin": str(e)}
            )

    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        """
        ID로 단일 객체 조회
        id_field가 설정되어 있어야 함함
        """
        if not self.id_field:
            raise DatabaseError(
                message="ID field is not configured for this model",
                detail={"model": self.model.__name__}
            )

        return session.exec(
            select(self.model).where(getattr(self.model, self.id_field) == id)
        ).first()

    def get_all(self, session: Session, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        전체 데이터 조회
        """
        return self.paginate(session, page, page_size)

    def update(self, session: Session, id: int, obj_in) -> Optional[T]:
        try:
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                raise NotFoundError(f"{self.model.__name__} with ID {id} not found")

            update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            session.add(db_obj)
            session.flush()
            session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            session.rollback()
            raise DatabaseError(
                message="Database integrity error during update()",
                detail={"origin": str(e)}
            )

    def delete(self, session: Session, id: int) -> Optional[T]:
        try:
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                raise NotFoundError(f"{self.model.__name__} with ID {id} not found")

            session.delete(db_obj)
            session.flush()
            return db_obj
        except IntegrityError as e:
            session.rollback()
            raise DatabaseError(
                message="Database integrity error during delete()",
                detail={"origin": str(e)}
            )

    def soft_delete(self, session: Session, id: int) -> Optional[T]:
        if not self.soft_delete_field:
            raise DatabaseError(
                message="Soft delete is not configured for this model",
                detail={"model": self.model.__name__}
            )

        try:
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                raise NotFoundError(f"{self.model.__name__} with ID {id} not found")

            setattr(db_obj, self.soft_delete_field, self.soft_delete_value)

            session.add(db_obj)
            session.flush()
            session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            session.rollback()
            raise DatabaseError(
                message="Database integrity error during soft delete",
                detail={"origin": str(e)}
            )

    def paginate(
        self, 
        session: Session, 
        page: int = 1, 
        page_size: int = 10,
        query = None
    ) -> Dict[str, Any]:
        """페이징 처리
        
        Args:
            session: DB 세션
            page: 페이지 번호 (기본값: 1)
            page_size: 페이지 크기 (기본값: 10)
            query: 커스텀 쿼리 (기본값: None)
            
        Returns:
            Dict[str, Any]: {
                "items": List[T],
                "pagination": {
                    "totalItems": int,
                    "totalPages": int,
                    "currentPage": int,
                    "pageSize": int
                }
            }
        """
        try:
            # 페이지 값 검증
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 10

            # 기본 쿼리 설정
            base_query = query if query else select(self.model)
            
            # 전체 개수 쿼리
            count_query = select(func.count()).select_from(base_query.subquery())
            total_count = session.exec(count_query).one()

            # 페이징 적용된 결과 쿼리
            results = session.exec(
                base_query
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()

            return {
                "items": results,
                "pagination": {
                    "totalItems": total_count,
                    "totalPages": (total_count + page_size - 1) // page_size,
                    "currentPage": page,
                    "pageSize": page_size
                }
            }

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to execute pagination query",
                detail={
                    "error": str(e),
                    "page": page,
                    "page_size": page_size
                }
            )
