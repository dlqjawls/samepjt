from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.admin import Admin
from typing import Optional
from fastapi import HTTPException

def get_admin_by_id(session: Session, admin_id: Optional[str]) -> Optional[Admin]:
    if not admin_id:
        raise HTTPException(status_code=400, detail="Admin ID cannot be None or empty")

    statement = select(Admin).where(Admin.adminId == admin_id)
    result = session.exec(statement).first()

    return result

def get_admin_by_pk(session: Session, admin_pk: Optional[int]) -> Optional[Admin]:
    if admin_pk is None:
        raise HTTPException(status_code=400, detail="Admin PK cannot be None")

    statement = select(Admin).where(Admin.adminPK == admin_pk)
    return session.exec(statement).first()

def create_admin(session: Session, admin_data: Admin) -> Admin:
    try:
        existing_admin = get_admin_by_id(session, admin_data.adminId)
        if existing_admin:
            raise HTTPException(status_code=400, detail=f"Admin with ID {admin_data.adminId} already exists")

        session.add(admin_data)
        session.commit()
        session.refresh(admin_data)
        return admin_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create admin")
