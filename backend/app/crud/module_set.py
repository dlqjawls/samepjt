from sqlmodel import Session, select
from app.models.module_set import ModuleSet
from app.crud.base import CRUDBase

class ModuleSetCRUD(CRUDBase[ModuleSet]):
    def __init__(self):
        super().__init__(ModuleSet, "module_set_id")

    def get_by_name(self, session: Session, module_set_name: str):
        statement = select(self.model).where(self.model.module_set_name == module_set_name)
        return session.exec(statement).first()

module_set_crud = ModuleSetCRUD()
