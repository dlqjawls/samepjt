from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from typing import Optional
from fastapi import HTTPException

def get_user_by_id(session: Session, user_id: Optional[str]) -> Optional[User]:
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID cannot be None or empty")

    statement = select(User).where(User.userId == user_id)
    result = session.exec(statement).first()
    
    return result

def get_user_by_pk(session: Session, user_pk: Optional[int]) -> Optional[User]:
    if user_pk is None:
        raise HTTPException(status_code=400, detail="User PK cannot be None")

    statement = select(User).where(User.userPK == user_pk)
    result = session.exec(statement).first()
    
    return result

def get_user_by_email(session: Session, user_email: Optional[str]) -> Optional[User]:
    if not user_email:
        raise HTTPException(status_code=400, detail="User email cannot be None or empty")

    statement = select(User).where(User.userEmail == user_email)
    return session.exec(statement).first()

def create_user(session: Session, user_data: User) -> User:
    try:
        existing_user = get_user_by_email(session, user_data.userEmail)
        if existing_user:
            raise HTTPException(status_code=400, detail=f"User with email {user_data.userEmail} already exists")

        session.add(user_data)
        session.commit()
        session.refresh(user_data)
        return user_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create user")