from sqlmodel import Session, select
from app.models.user import User
from app.crud.base import CRUDBase
from typing import Optional

class UserCRUD(CRUDBase[User]):
    def __init__(self):
        super().__init__(User, "user_pk")

    def get_user_by_user_id(self, session: Session, id: str) -> Optional[User]:
        statement = select(User).where(User.user_id == id)
        return session.exec(statement).first() 

    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.user_email == email)
        return session.exec(statement).first() 

    def get_user_role_name(self, role_id: int) -> str:
        """
        주어진 role_id에 해당하는 역할 이름을 반환합니다.
        LUT 상수를 가져오기 위해 app/crud/lut.py의 함수를 사용합니다.
        """
        from app.crud.lut import get_role_mapping
        role_mapping = get_role_mapping()
        return role_mapping.get(role_id, "Unknown")

user_crud = UserCRUD()
