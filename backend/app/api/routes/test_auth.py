from fastapi import APIRouter, Depends
from app.utils.jwt import  jwt_handler
from app.core.database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/test-auth")
async def test_auth(
    session: Session = Depends(get_session),
    token_data: dict = Depends(jwt_handler.jwt_auth_dependency())
):
    return {"message": "JWT 인증 성공", "user": token_data}

@router.post("/refresh-token")
async def refresh_token(
    refresh_token: str,
    session: Session = Depends(get_session)
):
    new_access_token = jwt_handler.refresh_access_token(refresh_token)
    return {"accessToken": new_access_token}

@router.post("/logout")
async def logout(
    session: Session = Depends(get_session),
    token_data: dict = Depends(jwt_handler.jwt_auth_dependency())
):
    user_pk = token_data["user_pk"]
    jwt_handler.delete_refresh_token(user_pk)
    return {"message": "Successfully logged out"}

@router.get("/admin-only")
async def admin_route(
    session: Session = Depends(get_session),
    token_data: dict = Depends(jwt_handler.jwt_auth_dependency(["master"]))
):
    return {"message": "관리자 전용 API", "user": token_data}

@router.get("/semi-admin")
async def semi_admin_route(
    session: Session = Depends(get_session),
    token_data: dict = Depends(jwt_handler.jwt_auth_dependency(["semi", "master"]))
):
    """✅ 세미 관리자 및 관리자만 접근 가능"""
    return {"message": "세미 관리자 및 관리자 전용 API", "user": token_data}

@router.get("/open-access")
async def open_access_route():
    """✅ 인증 없이 접근 가능"""
    return {"message": "이 API는 인증 없이 누구나 접근 가능"}
