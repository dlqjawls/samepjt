from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.auth_service import AuthService
from app.api.schemas.token import TokenRefreshRequest, TokenRefreshResponse, LogoutResponse
from app.core.jwt import jwt_handler

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/refresh-token", response_model=TokenRefreshResponse)
async def refresh_token(
    request: TokenRefreshRequest,  
    session: Session = Depends(get_session)
):
    """✅ 리프레시 토큰을 사용하여 새로운 액세스 토큰 및 리프레시 토큰을 발급"""
    return AuthService.refresh_access_token(session, request.refresh_token)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    session: Session = Depends(get_session),
    token_data: dict = Depends(jwt_handler.jwt_auth_dependency())
):
    """✅ 로그아웃 처리: 리프레시 토큰 삭제"""
    return AuthService.logout(session, token_data["user_pk"], token_data["role"])
