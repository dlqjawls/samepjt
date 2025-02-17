from sqlmodel import Session, select
from app.db.models.option_type import OptionType
from app.db.crud.base import CRUDBase
from typing import Optional


class OptionTypeCRUD(CRUDBase[OptionType]):
    def __init__(self):
        super().__init__(OptionType)
        
    def get_by_id(self, session: Session, option_type_id: int) -> Optional[OptionType]:
        """옵션 타입 ID에 해당하는 옵션 타입을 조회합니다."""
        option_type = session.exec(select(OptionType).where(OptionType.option_type_id == option_type_id)).first()
        return option_type 

    def get_option_name_by_id(self, session: Session, option_type_id: int) -> Optional[str]:
        """옵션 타입 ID에 해당하는 옵션 이름을 조회합니다.""" 
        option = session.exec(select(OptionType).where(OptionType.option_type_id == option_type_id)).first()
        return option.option_type_name if option else None


    def get_option_cost_by_id(self, session: Session, option_type_id: int) -> Optional[int]:
        """옵션 타입 ID에 해당하는 옵션 비용을 조회합니다."""
        option = session.exec(select(OptionType).where(OptionType.option_type_id == option_type_id)).first()
        return int(option.option_type_cost) if option else None


option_type_crud = OptionTypeCRUD()
