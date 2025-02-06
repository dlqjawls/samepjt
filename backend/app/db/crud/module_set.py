from sqlmodel import Session, select
from app.db.models.module_set import ModuleSet
from app.db.crud.base import CRUDBase

class ModuleSetCRUD(CRUDBase[ModuleSet]):
    def __init__(self):
        super().__init__(ModuleSet)

    def get_by_name(self, session: Session, module_set_name: str):
        """
        모듈 세트 이름으로 모듈 세트를 조회합니다.

        Args:
            session (Session): DB 세션
            module_set_name (str): 모듈 세트 이름
      
        Returns:
            ModuleSet: 조회된 모듈 세트 객체

        Raises:
            NotFoundError: 해당 이름의 모듈 세트가 없는 경우
            DatabaseError: DB 조회 중 오류 발생 시
        """
        statement = select(self.model).where(self.model.module_set_name == module_set_name)
        return session.exec(statement).first()


module_set_crud = ModuleSetCRUD()
