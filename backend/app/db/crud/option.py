from sqlalchemy import func
from sqlmodel import Session, select
from typing import List, Optional
from app.db.models.option import Option
from sqlalchemy.exc import SQLAlchemyError
from app.db.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError
from app.utils.lut_constants import ItemStatus

class OptionCRUD(CRUDBase[Option]):
    def __init__(self):
        super().__init__(Option)
        
    def get_by_id(self, session: Session, option_id: int) -> Optional[Option]:
        """주어진 ID에 해당하는 옵션을 조회합니다"""
        option = self.get_by_field(session, option_id, "option_id")
        return option

    def get_options_by_type(
        self,
        session: Session,
        option_type_id: int
    ) -> List[Option]:
        """특정 옵션 타입의 모든 옵션 객체를 조회합니다."""      
        query = select(self.model).where(
            self.model.option_type_id == option_type_id,
            self.model.deleted_at == None 
        )
        results = list(session.exec(query).all())
        return results
                    
    def get_available_options_by_type(
        self,
        session: Session,
        option_type_id: int,
        required_quantity: int,
        item_status_id: int = ItemStatus.INACTIVE.ID
    ) -> List[Option]:
        """특정 옵션 타입에서 사용 가능한 옵션을 조회합니다."""    
        query = select(self.model).where(
            self.model.option_type_id == option_type_id,
            self.model.item_status_id == item_status_id,
            self.model.deleted_at == None 
        ).limit(required_quantity)
        available_options = list(session.exec(query).all())
        return available_options

option_crud = OptionCRUD()