from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.module import Module
from app.db.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.lut_constants import ItemStatus

class ModuleCRUD(CRUDBase[Module]):
    def __init__(self):
        super().__init__(Module)
        
    def get_first_available_module(self, session: Session, status_id: int = ItemStatus.INACTIVE) -> Module:
        """첫 번째 사용 가능한 모듈을 조회합니다.

        Args:
            session (Session): DB 세션
            status_id (int, optional): 사용 가능한 모듈 상태 ID. Defaults to 2 (INACTIVE).

        Returns:
            Module: 첫 번째 사용 가능한 모듈 객체

        Raises:
            NotFoundError: 사용 가능한 모듈을 찾지 못한 경우
            DatabaseError: DB 조회 중 오류 발생 시
        """
        try:
            query = select(self.model).where(
                self.model.status_id == status_id,
                self.model.deleted_at == None
            ).limit(1)
            module = session.exec(query).first()
            if not module:
                raise NotFoundError(
                    message="No available module found",
                    detail={"status_id": status_id, "error": "모든 모듈이 사용 중입니다."}
                )
            return module
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch available module",
                detail={"error": str(e)}
            )        

module_crud = ModuleCRUD()