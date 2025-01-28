from sqlmodel import Session, select
from typing import List, Optional
from app.models.module import Module
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError

class ModuleCRUD(CRUDBase[Module]):
    def __init__(self):
        super().__init__(Module, "module_id")
        
    def get_modules_by_status(
        self, 
        session: Session, 
        status_id: int
    ) -> List[Module]:
        """
        특정 상태의 모듈 목록 조회

        Args:
            session: DB 세션
            status_id: 모듈 상태 ID

        Returns:
            List[Module]: 조회된 모듈 목록

        Raises:
            DatabaseError: 데이터베이스 조회 실패 시
        """
        try:
            query = (
                select(self.model)
                .where(self.model.status_id == status_id)
            )

            return list(session.exec(query).all())

        except Exception as e:
            raise DatabaseError(
                message="Failed to get modules by status",
                detail={
                    "status_id": status_id,
                    "error": str(e)
                }
            )

    def get_first_module_by_status_id(
        self, 
        session: Session,
        status_id: int,
    ) -> Module:
        """
        특정 상태에 해당하는 첫 번째 모듈 조회

        Args:
            session: DB 세션
            status_id: 모듈 상태 ID

        Returns:
            Module: 조회된 모듈

        Raises:
            DatabaseError: 모듈을 찾을 수 없거나 조회 실패 시
        """
        query = (
            select(self.model)
            .where(self.model.status_id == status_id)
        )

        module = session.exec(query).first()
        if module is None:
            raise DatabaseError(
                message="No available module found",
                detail={
                    "status_id": status_id
                }
            )
            
        return module

module_crud = ModuleCRUD()