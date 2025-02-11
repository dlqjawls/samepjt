from typing import Dict, Optional, TypeVar, Type, Generic, Any
from sqlmodel import SQLModel, Session, or_, select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
from app.utils.exceptions import DatabaseError, NotFoundError

T = TypeVar("T", bound=SQLModel)

class CRUDBase(Generic[T]):
    def __init__(self, model: Type[T]):
        """
        생성자

        Args:
            model (Type[T]): SQLModel 기반 모델 클래스.
        """
        self.model = model

    def base_query(self) -> Any:
        """
        기본 쿼리 생성 (soft delete가 있는 경우에만 필터링).

        Returns:
            Any: 기본 쿼리.
        """
        query = select(self.model)
        if hasattr(self.model, "deleted_at"):
            query = query.where(getattr(self.model, "deleted_at").is_(None))
        return query

    def get_by_field(self, session: Session, id_value: Any, id_field: str = "id") -> Optional[T]:
        """
        주어진 필드와 값을 기준으로 객체를 조회합니다.
        """
        try:
            return session.exec(self.base_query().where(getattr(self.model, id_field) == id_value)).first()
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to get object by field",
                detail={"error": str(e)}
            )

    def save(self, session: Session, obj: T) -> T:
        """
        객체를 DB에 저장하고 새 객체로 refresh하여 반환합니다.
        """
        session.add(obj)
        session.flush()
        session.refresh(obj)
        return obj

    def create(self, session: Session, obj_in) -> T:
        """
        객체를 생성합니다.

        Args:
            session (Session): DB 세션.
            obj_in (Pydantic 모델): 생성할 데이터.

        Raises:
            DatabaseError: 생성 도중 발생한 오류.

        Returns:
            T: 생성된 객체.
        """
        try:
            db_obj = self.model(**obj_in.dict())
            return self.save(session, db_obj)
        except IntegrityError as e:
            session.rollback()
            raise DatabaseError(
                message="객체 생성 오류.",
                detail={"origin": str(e)}
            )

    def update(self, session: Session, id_value: Any, obj_in, id_field: str = "id") -> Optional[T]:
        """
        객체를 업데이트합니다.

        Args:
            session (Session): DB 세션.
            id_value (Any): 업데이트할 객체의 ID 값.
            obj_in (dict 또는 Pydantic 모델): 업데이트할 데이터.
            id_field (str, optional): ID 필드명 (기본값: "id").

        Raises:
            NotFoundError: 객체를 찾지 못한 경우.
            DatabaseError: 업데이트 도중 발생한 오류.

        Returns:
            Optional[T]: 업데이트된 객체.
        """
        db_obj = self.get_by_field(session, id_value, id_field)
        if not db_obj:
            raise NotFoundError(f"{self.model.__name__} with {id_field}={id_value} not found")
        # obj_in이 딕셔너리이면 그대로 사용, 아니면 .dict()로 변환
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else obj_in
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        return self.save(session, db_obj)

    def soft_delete(self, session: Session, id_value: Any, id_field: str = "id") -> Optional[T]:
        """
        객체를 논리적으로 삭제합니다.

        Args:
            session (Session): DB 세션.
            id_value (Any): 삭제할 객체의 ID 값.
            id_field (str, optional): ID 필드명 (기본값: "id").

        Raises:
            NotFoundError: 객체를 찾지 못한 경우.
            DatabaseError: soft delete 기능 미구성 시.

        Returns:
            Optional[T]: 논리 삭제된 객체.
        """
        db_obj = self.get_by_field(session, id_value, id_field)
        if not db_obj:
            raise NotFoundError(f"{self.model.__name__} with {id_field}={id_value} not found")
        if not hasattr(db_obj, "deleted_at"):
            raise DatabaseError(
                message="Soft delete 기능 미구성 (deleted_at 없음).",
                detail={"model": self.model.__name__}
            )
        setattr(db_obj, "deleted_at", datetime.now())
        return self.save(session, db_obj)

    def hard_delete(self, session: Session, id_value: Any, id_field: str = "id") -> None:
        """
        객체를 영구적으로 삭제합니다.

        Args:
            session (Session): DB 세션.
            id_value (Any): 삭제할 객체의 ID 값.
            id_field (str, optional): ID 필드명 (기본값: "id").

        Raises:
            NotFoundError: 객체를 찾지 못한 경우.
        """
        db_obj = self.get_by_field(session, id_value, id_field)
        if not db_obj:
            raise NotFoundError(f"{self.model.__name__} with {id_field}={id_value} not found")
        session.delete(db_obj)
        session.flush()

    def paginate(self, session: Session, page: int = 1, page_size: int = 10, query: Any = None) -> Dict[str, Any]:
        """
        쿼리 결과를 페이지네이션합니다.

        Args:
            session (Session): DB 세션.
            page (int, optional): 페이지 번호.
            page_size (int, optional): 페이지당 항목 수.
            query (Any, optional): 커스텀 쿼리 (없으면 기본 쿼리 사용).

        Returns:
            Dict[str, Any]: 조회된 결과와 페이지네이션 정보.
        """
        try:
            page = max(page, 1)
            page_size = max(page_size, 1)
            base_query = query if query is not None else self.base_query()
            count_query = select(func.count()).select_from(base_query.subquery())
            total_count = session.exec(count_query).one()
            results = session.exec(
                base_query.offset((page - 1) * page_size).limit(page_size)
            ).all()
            return {
                "items": results,
                "pagination": {
                    "totalItems": total_count,
                    "totalPages": (total_count + page_size - 1) // page_size,
                    "currentPage": page,
                    "pageSize": page_size,
                }
            }
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="페이지네이션 처리 오류.",
                detail={"error": str(e), "page": page, "page_size": page_size}
            )

    def count_all(self, session: Session) -> int:
        """
        전체 객체 수를 조회합니다.

        Args:
            session (Session): DB 세션.

        Returns:
            int: 전체 객체 수.
        """
        base_query = self.base_query()
        count_query = select(func.count()).select_from(base_query.subquery())
        return session.exec(count_query).one()

    def get_list(
        self,
        session: Session,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        search: Optional[str] = None,
        search_fields: Optional[list] = None,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        필터링, 정렬, 검색을 적용하여 페이지네이션된 결과를 반환합니다.

        Args:
            session (Session): DB 세션.
            filters (Optional[Dict[str, Any]]): 필터 조건.
            sort_by (Optional[str]): 정렬할 필드명.
            order (str, optional): 정렬 순서 ("asc" 또는 "desc", 기본: "asc").
            search (Optional[str]): 검색어.
            search_fields (Optional[list]): 검색할 필드 목록.
            page (int, optional): 페이지 번호.
            page_size (int, optional): 페이지당 항목 수.

        Returns:
            Dict[str, Any]: 조회 결과와 페이지네이션 정보.
        """
        # 기본 쿼리 생성
        if include_deleted:
            query = select(self.model)
        else:
            query = self.base_query()

        # 필터 적용
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        # 검색 조건 적용 (검색할 필드가 지정되었을 경우)
        if search and search_fields:
            conditions = [
                getattr(self.model, field).ilike(f"%{search}%")
                for field in search_fields if hasattr(self.model, field)
            ]
            if conditions:
                query = query.where(or_(*conditions))

        # 정렬 조건 적용
        if sort_by and hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            column = column.desc() if order.lower() == "desc" else column.asc()
            query = query.order_by(column)

        # 페이지네이션 처리
        return self.paginate(session, page, page_size, query) 