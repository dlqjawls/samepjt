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

option_types_crud = OptionTypeCRUD()
