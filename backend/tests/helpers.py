from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.core.jwt import jwt_handler
import pytest

# GIVEN: 관리자 토큰 생성 (role "master")
@pytest.fixture
def master_token():
    return jwt_handler.create_token(1, role="master")[0]

# GIVEN: 일반 관리자 토큰 생성 (role "semi")
@pytest.fixture
def semi_admin_token():
    return jwt_handler.create_token(2, role="semi")[0]  

# GIVEN: 비관리자 토큰 생성 (role "user")
@pytest.fixture
def user_token():
    return jwt_handler.create_token(2, role="user")[0]


def register_and_login(
    client: TestClient,
    user_id: str = "testuser",
    password: str = "test1234"
) -> str:
    """테스트용 사용자 등록 및 로그인 후 access_token 반환
    
    Args:
        client: TestClient 인스턴스
        user_id: 사용자 ID (기본값: "testuser")
        password: 비밀번호 (기본값: "test1234")
        
    Returns:
        str: JWT access token
    """
    # 회원가입 요청
    register_payload = {
        "id": user_id,
        "password": password,
        "email": f"{user_id}@example.com",
        "name": f"{user_id}님",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    # 로그인 요청
    login_payload = {
        "id": user_id,
        "password": password
    }
    login_response = client.post("/auth/login", json=login_payload)
    return login_response.json()["data"]["access_token"]

def create_valid_rent_request(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """유효한 렌트 요청 데이터 생성
    
    Args:
        start_date: 렌트 시작일 (기본값: 현재 + 1일)
        end_date: 렌트 종료일 (기본값: 현재 + 2일)
        
    Returns:
        Dict: 렌트 요청 데이터
    """
    if not start_date:
        start_date = datetime.now() + timedelta(days=1)
    if not end_date:
        end_date = datetime.now() + timedelta(days=2)

    return {
        "selectedOptionTypes": [
            {"optionTypeId": 1, "quantity": 1},
            {"optionTypeId": 2, "quantity": 1}
        ],
        "autonomousArrivalPoint": {"x": 12.313, "y": 32.3232},
        "autonomousDeparturePoint": {"x": 11.512, "y": 30.4531},
        "rentStartDate": start_date.isoformat(),
        "rentEndDate": end_date.isoformat()
    }

def create_test_rent(client: TestClient, access_token: str) -> int:
    """렌트 요청을 생성하고 rent_id 반환
    
    Args:
        client: TestClient 인스턴스
        access_token: JWT access token
        
    Returns:
        int: 생성된 렌트 ID
    """
    rent_request = create_valid_rent_request()
    response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()["data"]["rent_id"]