from fastapi import APIRouter
from app.models.user import UserRegisterRequest, UserRegisterResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/user/register", response_model=UserRegisterResponse)
def register_user(user: UserRegisterRequest):
    return UserService.register_user(user)
