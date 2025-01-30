from sqlmodel import Session, select
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.models.module import Module
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError

class ModuleCRUD(CRUDBase[Module]):
    def __init__(self):
        super().__init__(Module, "module_id")    
        
    def get_first_available_module(
        self,
        session: Session,
        status_id: int = 2  # INACTIVE
    ) -> Module:
        """첫 번째 사용 가능한 모듈 조회"""
        try:
            module = session.exec(
                select(self.model)
                .where(
                    self.model.status_id == status_id,
                    self.model.deleted_at == None
                )
                .limit(1)
            ).first()

            if not module:
                raise NotFoundError(
                    message="No available module found",
                    detail={
                        "status_id": status_id,
                        "error": "모든 모듈이 사용 중입니다."
                    }
                )

            return module

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch available module",
                detail={"error": str(e)}
            )        
        
module_crud = ModuleCRUD()