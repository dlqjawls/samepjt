import pytest
from datetime import datetime
from app.core.jwt import jwt_handler
from app.db.models.vehicle import Vehicle
from sqlmodel import Session, select
from app.utils.lut_constants import ItemStatus
from tests.helpers import master_token, semi_admin_token, user_token, create_dummy_vehicles


def test_update_vehicle_success(client, session, master_token, create_dummy_vehicles):
    """정상적인 차량 정보 업데이트 테스트"""
    # 더미 차량 1건 생성
    vehicles = create_dummy_vehicles(1)
    vehicle = vehicles[0]
    update_data = {
        "vehicle_number": "PBV-9999", # 차량 번호 업데이트
    }
    response = client.patch(
        f"/api/admin/vehicles/{vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # 응답 검증
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Vehicle updated successfully"
    
    # DB에 변경 내용 반영 여부 검증
    updated_vehicle = session.get(Vehicle, vehicle.vehicle_id)
    assert updated_vehicle.vehicle_number == "PBV-9999"

def test_update_vehicle_unauthorized(client, create_dummy_vehicles):
    """인증 토큰 없이 차량 정보 업데이트 시도 테스트"""
    vehicles = create_dummy_vehicles(1)
    vehicle = vehicles[0]
    update_data = {
        "vehicle_number": "PBV-9999"
    }
    response = client.patch(
        f"/api/admin/vehicles/{vehicle.vehicle_id}",
        json=update_data
    )
    assert response.status_code == 401

def test_update_vehicle_forbidden(client, create_dummy_vehicles, user_token):
    """비관리자 토큰으로 차량 정보 업데이트 시도 테스트"""
    vehicles = create_dummy_vehicles(1)
    vehicle = vehicles[0]
    update_data = {
        "vehicle_number": "PBV-9999"
    }
    response = client.patch(
        f"/api/admin/vehicles/{vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_update_nonexistent_vehicle(client, master_token):
    """존재하지 않는 차량 정보 업데이트 시도 테스트"""
    update_data = {
        "vehicle_number": "PBV-9999"
    }
    response = client.patch(
        "/api/admin/vehicles/99999",  # 존재하지 않는 차량 ID
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Vehicle not found" in data["message"]

@pytest.mark.parametrize("invalid_vehicle_id", ["abc", -1, 0])
def test_update_vehicle_invalid_id(client, master_token, invalid_vehicle_id):
    """잘못된 형식의 차량 ID로 업데이트 시도 테스트"""
    update_data = {
        "vehicle_number": "PBV-9999"
    }
    response = client.patch(
        f"/api/admin/vehicles/{invalid_vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # Pydantic 유효성 검사 실패 시 422 에러 발생
    assert response.status_code == 422

@pytest.mark.parametrize("invalid_number", [
    "PBV1234",  # 하이픈 없음
    "PBV-123",  # 숫자 3자리
    "PBV-12345",  # 숫자 5자리
    "ABC-1234",  # 잘못된 접두사
    "pbv-1234",  # 소문자
    "PBV-123A",  # 문자 포함
    " PBV-1234 "  # 앞뒤 공백
])
def test_update_vehicle_invalid_number_format(client, master_token, create_dummy_vehicles, invalid_number):
    """잘못된 형식의 차량 번호로 업데이트 시도 테스트"""
    vehicles = create_dummy_vehicles(1)
    vehicle = vehicles[0]
    update_data = {
        "vehicle_number": invalid_number
    }

    response = client.patch(
        f"/api/admin/vehicles/{vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation error" in data["message"].lower()

def test_update_vehicle_duplicate_number(client, session, master_token, create_dummy_vehicles):
    """중복된 차량 번호로 업데이트 시도 테스트"""
    vehicles = create_dummy_vehicles(2)
    vehicle = vehicles[0]
    other_vehicle = vehicles[1]
    update_data = {
        "vehicle_number": other_vehicle.vehicle_number
    }

    response = client.patch(
        f"/api/admin/vehicles/{vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
  
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"].lower()
