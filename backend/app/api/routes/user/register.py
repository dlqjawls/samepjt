from fastapi import APIRouter, Depends
from app.core.database import Session, get_session
from app.api.schemas.user.register import UserRegisterRequest, UserRegisterResponse
from app.services.user.register import UserRegisterService

router = APIRouter()

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    summary="회원가입",
    description="새로운 사용자를 등록합니다.",
    responses={
        200: {
            "description": "회원가입 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "User registered successfully",
                        "errors": []
                    }
                }
            }
        },
        400: {
            "description": "회원가입 실패 - 중복된 ID 또는 이메일",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "User registration failed",
                        "errors": [
                            {"field": "userId", "message": "User ID already exists"},
                            {"field": "userEmail", "message": "Email is already registered"}
                        ]
                    }
                }
            },
        },
        422: {
            "description": "유효성 검사 실패 - 요청 형식 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "userId"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            },
                            {
                                "loc": ["body", "userPassword"],
                                "msg": "ensure this value has at least 6 characters",
                                "type": "value_error.any_str.min_length",
                            }
                        ]
                    }
                }
            },
        },
    },
)
def user_register(user_register_req: UserRegisterRequest, session: Session = Depends(get_session)):
    """ 사용자 회원가입 API """
    return UserRegisterService.register_user(user_register_req, session)
