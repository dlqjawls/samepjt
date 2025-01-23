from sqlmodel import select, Session
from app.models.user import User
from typing import Union, List

def get_user_by_id(session: Session, user_id: int) -> Union[User, None]:
    statement = select(User).where(User.userId == user_id)
    return session.exec(statement).first()

def get_all_users(session: Session) -> List[User]:
    statement = select(User)
    return list(session.exec(statement).all())

def create_user(session: Session, user_data: User) -> User:
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data

def update_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()