from sqlmodel import select, Session
from app.models.admin import Admin
from typing import Union

def get_admin_by_admin_id(session: Session, admin_id: str) -> Union[Admin, None]:
    statement = select(Admin).where(Admin.adminId == admin_id)
    return session.exec(statement).first()

def create_admin(session: Session, admin_data: Admin) -> Admin:
    session.add(admin_data)
    session.commit()
    session.refresh(admin_data)
    return admin_data

def update_admin(session: Session, admin: Admin) -> Admin:
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin

def delete_admin(session: Session, admin: Admin) -> None:
    session.delete(admin)
    session.commit()
