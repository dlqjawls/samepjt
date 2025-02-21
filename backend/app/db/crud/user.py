from sqlmodel import Session
from typing import Optional
from app.db.models.user import User
from app.db.crud.base import CRUDBase

class UserCRUD(CRUDBase[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_id(self, session: Session, id: str) -> Optional[User]:
        """
        주어진 ID에 해당하는 사용자를 조회합니다.

        Args:
            session (Session): 데이터베이스 세션.
            id (int): 사용자 ID.

        Returns:
            Optional[User]: 사용자 객체.
        """
        return self.get_by_field(session, id, "user_id")

    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        """
        주어진 이메일에 해당하는 사용자를 조회합니다.

        Args:
            session (Session): 데이터베이스 세션.
            email (str): 사용자 이메일.

        Returns:
            Optional[User]: 사용자 객체.
        """
        return self.get_by_field(session, email, "user_email")

user_crud = UserCRUD()
