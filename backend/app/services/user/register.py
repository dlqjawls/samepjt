from fastapi import HTTPException
from app.models.user import User
from app.api.schemas.user.register import UserRegisterRequest, UserRegisterResponse
from app.core.database import get_session
from app.utils.bcrypt import hash_password
from datetime import datetime
from sqlmodel import select

class UserRegisterService:
    """ 사용자 회원가입 서비스 클래스 """

    @staticmethod
    def register_user(user: UserRegisterRequest) -> UserRegisterResponse:
        """ 새로운 사용자를 등록합니다 """
        with get_session() as session:
            errors = []

            # 중복 검사
            statement = select(User).where(User.userId == user.userId)
            if session.exec(statement).first():
                errors.append({"field": "userId", "message": "User ID already exists"})
            
            statement = select(User).where(User.userEmail == user.userEmail)
            if session.exec(statement).first():
                errors.append({"field": "userEmail", "message": "Email is already registered"})
            
            # 필수 입력값 검증
            if not user.userEmail.strip():
                errors.append({"field": "userEmail", "message": "Email is required"})

            # 유효성 검사 실패 시 예외 발생
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

            # 새로운 사용자 추가
            new_user = User(
                userId=user.userId,
                userPassword=hashed_password,
                userEmail=user.userEmail,
                userName=user.userName,
                userPhoneNum=user.userPhoneNum,
                userAddress=user.userAddress,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully", errors=[])