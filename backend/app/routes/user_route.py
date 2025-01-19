from fastapi import APIRouter
from app.models.user import UserRegisterRequest, UserRegisterResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/user/register", response_model=UserRegisterResponse)
def register_user(user: UserRegisterRequest):
    """
    회원가입 API 엔드포인트

    요청 데이터를 받아 사용자 계정을 등록하는 API입니다.

    Args:
        user (UserRegisterRequest): 회원가입 요청 데이터 (Pydantic 모델)

    Returns:
        UserRegisterResponse: 회원가입 응답 데이터 (Pydantic 모델)
    
    예제 요청:
    ```
    POST /user/register
    {
        "userId": "testUser",
        "userPassword": "securePassword123",
        "userEmail": "test@example.com",
        "userName": "Test User",
        "userPhoneNum": "010-1234-5678",
        "userAddress": "Seoul, South Korea"
    }
    ```

    예제 응답 (성공 시):
    ```
    {
        "resultCode": "SUCCESS",
        "message": "User registered successfully"
    }
    ```

    예제 응답 (실패 시):
    ```
    {
        "resultCode": "FAILURE",
        "message": "User registration failed",
        "errors": [
            {"field": "userId", "message": "User ID already exists"}
        ]
    }
    ```
    """
    return UserService.register_user(user)
