from fastapi import APIRouter
from app.models.user import UserRegisterRequest, UserRegisterResponse
from app.services.user_service import UserService
from app.dummy_data import dummy_users  # 더미 데이터

router = APIRouter()

@router.get("/user/list")
def get_user_list():
    """
    개발용: 더미 사용자 데이터를 확인하는 API

    Returns:
        List[dict]: 더미 사용자 데이터 목록
    
    예제 응답:
    ```
    GET /user/list
    [
        {
            "userId": "john_doe",
            "userPassword": "securepassword",
            "userEmail": "john@example.com",
            "userName": "John Doe",
            "userPhoneNum": "010-1234-5678",
            "userAddress": "123 Main St, City, Country"
        }
    ]
    ```
    """
    return dummy_users

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
