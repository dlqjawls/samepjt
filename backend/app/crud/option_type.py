from sqlmodel import Session, col, select, func
from app.models.option_type import OptionType
from app.models.option import Option
from app.crud.base import CRUDBase

class OptionTypeCRUD(CRUDBase[OptionType]):
    def __init__(self):
        super().__init__(OptionType, "option_type_id")

    def get_option_counts_by_type(self, session: Session) -> dict:
        statement = (
            select(Option.option_type_id, func.count())
            .group_by(Option.option_type_id)
        )
        return dict(session.exec(statement).all())

    def get_option_type_name(self, option_type_id: int) -> str:
        """
        주어진 옵션 타입 ID에 해당하는 이름을 반환합니다.
        (여기서는 ITEM_TYPE_MAPPING을 활용합니다.)
        """
        from app.crud.lut import get_item_type_mapping
        mapping = get_item_type_mapping()
        return mapping.get(option_type_id, "Unknown")

option_types_crud = OptionTypeCRUD()
