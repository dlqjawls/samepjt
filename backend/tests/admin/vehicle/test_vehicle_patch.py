import pytest
from datetime import datetime
from app.core.jwt import jwt_handler
from app.db.models.vehicle import Vehicle
from sqlmodel import Session, select
from app.utils.lut_constants import ItemStatus

@pytest.fixture
def master_token():
    """마스터 권한 토큰 생성"""
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    """일반 관리자 권한 토큰 생성"""
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def test_vehicle(session: Session):
    """테스트용 차량 데이터 생성"""
    vehicle = Vehicle(
        vin="TEST123456789",
        vehicle_number="PBV-1234",
        current_location='{"x": 12.313, "y": 32.3232}',
        item_status_id=ItemStatus.ACTIVE,
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()

    )
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle

def test_update_vehicle_success(client, session, master_token, test_vehicle):
    """✅ 정상적인 차량 정보 업데이트 테스트"""
    # Given: 업데이트할 차량 데이터
    update_data = {
        "vehicle_number": "PBV-5678",
        "last_maintenance_at": "2024-03-15T10:00:00",
        "next_maintenance_at": "2024-09-15T10:00:00"
    }

    # When: 마스터 권한으로 차량 정보 업데이트 요청
    response = client.patch(
        f"/admin/vehicles/{test_vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Vehicle updated successfully"

    # Then: DB에 저장된 데이터 검증
    updated_vehicle = session.exec(
        select(Vehicle).where(Vehicle.vehicle_id == test_vehicle.vehicle_id)
    ).first()
    assert updated_vehicle.vehicle_number == update_data["vehicle_number"]

def test_update_vehicle_unauthorized(client, test_vehicle, semi_admin_token):
    """❌ 권한 없는 사용자의 차량 정보 업데이트 시도"""
    update_data = {
        "vehicle_number": "PBV-5678"
    }

    response = client.patch(
        f"/admin/vehicles/{test_vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Permission denied" in data["message"]

def test_update_nonexistent_vehicle(client, master_token):
    """❌ 존재하지 않는 차량 정보 업데이트 시도"""
    update_data = {
        "vehicle_number": "PBV-5678"
    }

    response = client.patch(
        "/admin/vehicles/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Vehicle not found" in data["message"]

@pytest.mark.parametrize("invalid_number", [
    "PBV1234",  # 하이픈 없음
    "PBV-123",  # 숫자 3자리
    "PBV-12345",  # 숫자 5자리
    "ABC-1234",  # 잘못된 접두사
    "pbv-1234",  # 소문자
    "PBV-123A",  # 문자 포함
    " PBV-1234 "  # 앞뒤 공백
])
def test_update_vehicle_invalid_number_format(client, master_token, test_vehicle, invalid_number):
    """❌ 잘못된 형식의 차량 번호로 업데이트 시도"""
    update_data = {
        "vehicle_number": invalid_number
    }

    response = client.patch(
        f"/admin/vehicles/{test_vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation error" in data["message"].lower()

def test_update_vehicle_duplicate_number(client, session, master_token, test_vehicle):
    """❌ 중복된 차량 번호로 업데이트 시도"""
    # Given: 다른 차량 데이터 생성
    other_vehicle = Vehicle(
        vin="OTHER123456789",
        vehicle_number="PBV-9999",
        current_location='{"x": 12.313, "y": 32.3232}',
        item_status_id=ItemStatus.ACTIVE,
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()

    )
    session.add(other_vehicle)
    session.commit()

    # When: 이미 존재하는 차량 번호로 업데이트 시도
    update_data = {
        "vehicle_number": "PBV-9999"
    }

    response = client.patch(
        f"/admin/vehicles/{test_vehicle.vehicle_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 409 Conflict 응답 검증
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"].lower()

def test_update_vehicle_without_token(client, test_vehicle):
    """❌ 인증 토큰 없이 차량 정보 업데이트 시도"""
    update_data = {
        "vehicle_number": "PBV-5678"
    }

    response = client.patch(
        f"/admin/vehicles/{test_vehicle.vehicle_id}",
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Authentication" in data["message"]
