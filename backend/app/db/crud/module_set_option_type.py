from sqlmodel import Session, select
from app.db.models.module_set_option_types import ModuleSetOptionTypes
from app.db.crud.base import CRUDBase
from typing import List

class ModuleSetOptionTypesCRUD(CRUDBase[ModuleSetOptionTypes]):
    def __init__(self): 
        super().__init__(ModuleSetOptionTypes)

    def get_option_types_by_module_set(
        self,
        session: Session,
        module_set_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> List[ModuleSetOptionTypes]:
        """모듈 세트에 속한 옵션 타입들을 조회합니다."""
        query = select(self.model).where(self.model.module_set_id == module_set_id)
        return list(session.exec(query).all())
      
    def get_module_sets_by_option_type(
        self,
        session: Session,
        option_type_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> List[ModuleSetOptionTypes]:
        """특정 옵션 타입에 속한 모듈 세트들을 조회합니다."""
        query = select(self.model).where(self.model.option_type_id == option_type_id)
        return list(session.exec(query).all())
      
    def delete_by_module_set_id(
        self,
        session: Session,
        module_set_id: int
    ) -> None:
        """모듈 세트 ID에 해당하는 모든 옵션 타입 삭제"""
        session.query(self.model).filter(self.model.module_set_id == module_set_id).delete()  # type: ignore

    def delete_by_option_type_id(
        self,
        session: Session,
        option_type_id: int
    ) -> None:
        """옵션 타입 ID에 해당하는 모든 옵션 타입 삭제"""
        session.query(self.model).filter(self.model.option_type_id == option_type_id).delete()  # type: ignore
        
    def delete_by_module_set_id_and_option_type_id(
        self,
        session: Session,
        module_set_id: int,
        option_type_id: int
    ) -> None:
        """모듈 세트 ID와 옵션 타입 ID에 해당하는 옵션 타입 삭제""" 
        session.query(self.model).filter(self.model.module_set_id == module_set_id, self.model.option_type_id == option_type_id).delete()  # type: ignore   


module_set_option_type_crud = ModuleSetOptionTypesCRUD()