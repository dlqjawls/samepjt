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
        
    def get_module_type_name(self, module_type_id: int) -> str:
        """
        주어진 모듈 유형 ID에 해당하는 'name' 값을 반환합니다.
        """
        from app.crud.lut import get_module_type_mapping
        mapping = get_module_type_mapping()
        # mapping에는 {id: {"name": ..., ...}} 형태이므로 "name" 키를 추출합니다.
        return mapping.get(module_type_id, {}).get("name", "Unknown")

module_crud = ModuleCRUD()