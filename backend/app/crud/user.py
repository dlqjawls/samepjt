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

user_crud = UserCRUD()
