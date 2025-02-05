from sqlmodel import Session, select
from app.models.module_set import ModuleSet
from app.crud.base import CRUDBase

class ModuleSetCRUD(CRUDBase[ModuleSet]):
    def __init__(self):
        super().__init__(ModuleSet, "module_set_id")

    def get_by_name(self, session: Session, module_set_name: str):
        statement = select(self.model).where(self.model.module_set_name == module_set_name)
        return session.exec(statement).first()

    def get_item_status_name(self, status_id: int) -> str:
        """
        모듈 세트 관련 기능에서 사용될 수 있는 아이템 상태 이름을 반환합니다.
        """
        from app.crud.lut import get_item_status_mapping
        mapping = get_item_status_mapping()
        return mapping.get(status_id, "Unknown")

module_set_crud = ModuleSetCRUD()
