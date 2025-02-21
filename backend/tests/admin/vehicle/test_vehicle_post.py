import pytest
from sqlmodel import Session, select, text, delete
from app.db.models.vehicle import Vehicle
from app.core.jwt import jwt_handler
from app.utils.lut_constants import ItemStatus
from tests.helpers import master_token, user_token, create_dummy_vehicles


def test_create_vehicle_success(client, session, master_token):
    """정상적인 차량 등록 테스트"""
    vehicle_data = {
        "vin": "TEST123456789",
        "vehicle_number": "PBV-1234",
    }
    response = client.post(
        "/api/admin/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Vehicle registered successfully"
    
    stmt = select(Vehicle).where(Vehicle.vin == vehicle_data["vin"])
    registered_vehicle = session.exec(stmt).first()
    assert registered_vehicle is not None
    assert registered_vehicle.vehicle_number == vehicle_data["vehicle_number"]
    assert registered_vehicle.item_status_id == ItemStatus.INACTIVE.ID
    assert registered_vehicle.mileage == 0.0

def test_create_vehicle_unauthorized(client):
    """인증 없이 차량 등록 시도"""
    vehicle_data = {
        "vin": "TEST123456789",
        "vehicle_number": "PBV-1234",
    }
    response = client.post(
        "/api/admin/vehicles",
        json=vehicle_data
    )
    assert response.status_code == 401

def test_create_vehicle_forbidden(client, user_token):
    """권한 없는 사용자의 차량 등록 시도"""    
    vehicle_data = {
        "vin": "TEST123456789",
        "vehicle_number": "PBV-1234",
    }
    response = client.post(
        "/api/admin/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    
def test_create_vehicle_duplicate_vin(client, session, master_token, create_dummy_vehicles):
    """중복된 VIN으로 차량 등록 시도"""
    vehicles = create_dummy_vehicles(1)
    vehicle = vehicles[0]
    duplicate_data = {
        "vin": vehicle.vin,
        "vehicle_number": "PBV-1234",
    }
    response = client.post(
        "/api/admin/vehicles",
        json=duplicate_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"].lower()
    
    
def test_create_vehicle_duplicate_vehicle_number(client, session, master_token, create_dummy_vehicles):
    """중복된 차량 번호로 등록 시도"""
    vehicles = create_dummy_vehicles(1)
    vehicle = vehicles[0]
    duplicate_data = {
        "vin": "TEST123456789",
        "vehicle_number": vehicle.vehicle_number
    }
    response = client.post(
        "/api/admin/vehicles",
        json=duplicate_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"]
    assert data["detail"]["vehicle_number"] == duplicate_data["vehicle_number"]


@pytest.mark.parametrize("invalid_vin", [
    "",  # 빈 문자열
    "A" * 51,  # 최대 길이 초과
    "TEST@123",  # 특수문자 포함
    "TEST 123",  # 공백 포함
    "TEST-123",  # 하이픈 포함
    "TEST_123",  # 언더스코어 포함
])
def test_create_vehicle_invalid_vin_format(client, master_token, invalid_vin):
    """잘못된 VIN 형식으로 등록 시도"""
    vehicle_data = {
        "vin": invalid_vin,
        "vehicle_number": "PBV-1234"
    }
    response = client.post(
        "/api/admin/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

@pytest.mark.parametrize("invalid_number", [
    "PBV1234",  # 하이픈 없음
    "PBV-123",  # 숫자 3자리
    "PBV-12345",  # 숫자 5자리
    "ABC-1234",  # 잘못된 접두사
    "pbv-1234",  # 소문자
    "PBV-123A",  # 문자 포함
    " PBV-1234 "  # 앞뒤 공백
])
def test_create_vehicle_invalid_number_format(client, master_token, invalid_number):
    """잘못된 차량 번호 형식으로 등록 시도"""
    vehicle_data = {
        "vin": "TEST123456789",
        "vehicle_number": invalid_number
    }
    response = client.post(
        "/api/admin/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

@pytest.mark.parametrize("missing_field", [
    {"vehicle_number": "PBV-1234"},
    {"vin": "TEST123456789"},
    {}
])
def test_create_vehicle_missing_fields(client, master_token, missing_field):
    """필수 필드 누락 테스트"""
    response = client.post(
        "/api/admin/vehicles",
        json=missing_field,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"

def test_create_multiple_vehicles_success(client, session, master_token):
    """여러 차량 연속 등록 테스트"""
    vehicles_data = [
        {"vin": f"TEST{i}", "vehicle_number": f"PBV-{i:04d}"}
        for i in range(1, 4)
    ]

    for vehicle_data in vehicles_data:
        response = client.post(
            "/admin/vehicles",
            json=vehicle_data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["resultCode"] == "SUCCESS"

    # DB에 모든 차량이 저장되었는지 확인
    for vehicle_data in vehicles_data:
        vehicle = session.exec(
            select(Vehicle).where(Vehicle.vin == vehicle_data["vin"])
        ).first()
        assert vehicle is not None
        assert vehicle.vehicle_number == vehicle_data["vehicle_number"]
