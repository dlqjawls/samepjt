from app.core.jwt import jwt_handler
from sqlmodel import Session

class AuthService:
    @staticmethod
    def refresh_access_token(session: Session, refresh_token: str):
        new_access_token, new_refresh_token = jwt_handler.refresh_access_token(refresh_token)
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}

    @staticmethod
    def logout(session: Session, user_pk: int, role: str):
        jwt_handler.delete_refresh_token(user_pk, role)
        return {"message": "Successfully logged out"}
