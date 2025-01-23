from fastapi import HTTPException
from sqlmodel import Session
from app.crud.user import get_user_by_email, get_user_by_id, create_user
from app.models.user import User
from app.api.schemas.user.register import UserRegisterRequest, UserRegisterResponse
from app.utils.bcrypt import hash_password
from datetime import datetime

class UserRegisterService:

    @staticmethod
    def register_user(user: UserRegisterRequest, session: Session) -> UserRegisterResponse:
        errors = []

        # 중복 검사
        try:
            if get_user_by_id(session, user.userId):
                errors.append({"field": "userId", "message": "User ID already exists"})
        except Exception as e:
            pass 

        try:
            if get_user_by_email(session, user.userEmail):
                errors.append({"field": "userEmail", "message": "Email is already registered"})
        except Exception as e:
            pass 

        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "resultCode": "FAILURE",
                    "message": "User registration failed",
                    "errors": errors
                }
            )

        # 비밀번호 해싱 후 저장
        hashed_password = hash_password(user.userPassword)

        # 새로운 사용자 추가 (CRUD 함수 호출)
        new_user = User(
            userId=user.userId,
            userPassword=hashed_password,
            userEmail=user.userEmail,
            userName=user.userName,
            userPhoneNum=user.userPhoneNum,
            userAddress=user.userAddress,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
        )

        try:
            create_user(session, new_user)
        except ValueError as e:
            session.rollback()
            raise HTTPException(status_code=400, detail={"resultCode": "FAILURE", "message": str(e)})
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail={"resultCode": "ERROR", "message": "Database error occurred"}
            ) from e

        return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully", errors=[])
