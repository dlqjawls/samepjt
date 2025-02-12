from sqlmodel import Session, select
from app.db.models.module_set_option_types import ModuleSetOptionTypes
from app.db.crud.base import CRUDBase
from app.utils.exceptions import NotFoundError, ValidationError

class ModuleSetOptionTypesCRUD(CRUDBase[ModuleSetOptionTypes]):
    def __init__(self): 
        super().__init__(ModuleSetOptionTypes)

    def get_option_types_by_module_set(
        self,
        session: Session,
        module_set_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """모듈 세트에 속한 옵션 타입들을 페이지네이션과 함께 조회합니다.

        Args:
            session (Session): DB 세션
            module_set_id (int): 모듈 세트 ID
            page (int, optional): 페이지 번호. Defaults to 1.
            page_size (int, optional): 페이지 크기. Defaults to 10.

        Returns:
            dict: {'items': List[ModuleSetOptionType], 'pagination': {...}}

        Raises:
            ValidationError: 잘못된 모듈 세트 ID가 전달된 경우
            NotFoundError: 해당 모듈 세트에 대응하는 옵션 타입이 없는 경우
            DatabaseError: DB 조회 중 오류 발생 시
        """
        if module_set_id <= 0:
            raise ValidationError(
                message="Invalid module set ID",
                detail={"module_set_id": module_set_id, "error": "Module set ID must be positive"}
            )

        query = select(self.model).where(self.model.module_set_id == module_set_id)
        paginated = self.paginate(session=session, page=page, page_size=page_size, query=query)
        return paginated
      
    def get_module_sets_by_option_type(
        self,
        session: Session,
        option_type_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """특정 옵션 타입에 속한 모듈 세트들을 페이지네이션과 함께 조회합니다.

        Args:
            session (Session): DB 세션
            option_type_id (int): 옵션 타입 ID
            page (int, optional): 페이지 번호. Defaults to 1.
            page_size (int, optional): 페이지 크기. Defaults to 10.

        Returns:
            dict: {'items': List[ModuleSetOptionType], 'pagination': {...}}

        Raises:
            ValidationError: 잘못된 옵션 타입 ID가 전달된 경우
            NotFoundError: 해당 옵션 타입에 대응하는 모듈 세트가 없는 경우
            DatabaseError: DB 조회 중 오류 발생 시
        """
        if option_type_id <= 0:
            raise ValidationError(
                message="Invalid option type ID",
                detail={"option_type_id": option_type_id, "error": "Option type ID must be positive"}
            )

        query = select(self.model).where(self.model.option_type_id == option_type_id)
        paginated = self.paginate(session=session, page=page, page_size=page_size, query=query)
        return paginated
      
      
    def delete_by_module_set_id(
        self,
        session: Session,
        module_set_id: int
    ) -> None:
        """모듈 세트 ID에 해당하는 모든 옵션 타입 삭제"""
        session.query(self.model).filter(self.model.module_set_id == module_set_id).delete()  # type: ignore

module_set_option_type_crud = ModuleSetOptionTypesCRUD()