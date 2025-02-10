import pytest
from datetime import datetime
from sqlmodel import Session
from app.db.models.vehicle import Vehicle
from app.core.jwt import jwt_handler
from sqlalchemy import text
import json

from app.utils.lut_constants import ItemStatus

# GIVEN: 관리자 토큰 생성 (role "master")
@pytest.fixture
def admin_token():
    return jwt_handler.create_token(1, role="master")[0]

# GIVEN: 비관리자 토큰 생성 (role "user")
@pytest.fixture
def non_admin_token():
    return jwt_handler.create_token(2, role="user")[0]

# GIVEN: 차량 테이블 초기화 헬퍼
@pytest.fixture
def clear_vehicles(session: Session):
    def _clear():
        session.exec(text("DELETE FROM vehicle"))
        session.commit()
    return _clear

# GIVEN: 더미 차량 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_vehicles(session: Session):
    def _create(count: int = 3):
        vehicles = []
        for i in range(count):
            # JSON 형식의 좌표 문자열 생성
            location = json.dumps({"x": 12.313, "y": 32.3232})
            vehicle = Vehicle(
                vin=f"VIN{i+1}",
                vehicle_number=f"NUM{i+1}",
                current_location=location,  # JSON 문자열로 저장
                mileage=1000.0 * (i+1),
                last_maintenance_at=datetime.now(),
                next_maintenance_at=datetime.now(),
                item_status_id=ItemStatus.ACTIVE,
                created_by=1,
                updated_by=1

            )
            session.add(vehicle)
            vehicles.append(vehicle)
        session.commit()
        return vehicles
    return _create

def test_get_vehicle_list_success(client, session, create_dummy_vehicles, admin_token):
    # GIVEN: 관리자 토큰과 3개의 더미 차량 데이터가 준비됨
    create_dummy_vehicles(3)
    
    # WHEN: /admin/vehicles 엔드포인트를 GET 요청
    response = client.get(
        "/admin/vehicles?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # THEN: 응답이 성공적이고, 각 차량 필드가 올바르게 매핑됨
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "vehicles" in data["data"]
    vehicles = data["data"]["vehicles"]
    assert isinstance(vehicles, list)
    assert len(vehicles) >= 3
    
    # 첫 번째 차량 데이터 검증
    vehicle = vehicles[0]
    assert "vehicle_id" in vehicle
    assert "vin" in vehicle
    assert "vehicle_number" in vehicle
    assert isinstance(vehicle["current_location"], dict)
    assert "x" in vehicle["current_location"]
    assert "y" in vehicle["current_location"]

def test_get_vehicle_list_unauthorized(client):
    # 인증 토큰 없이 호출 시 401 Unauthorized 반환 확인
    response = client.get("/admin/vehicles?page=1&pageSize=10")
    assert response.status_code == 401

def test_get_vehicle_list_non_admin(client, session, create_dummy_vehicles, non_admin_token):
    # GIVEN: 비관리자 토큰과 3개의 더미 차량 데이터가 준비됨
    create_dummy_vehicles(3)

    # WHEN: /admin/vehicles 엔드포인트를 비관리자 토큰으로 호출
    response = client.get(
        "/admin/vehicles?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    # THEN: 403 Forbidden 응답이 발생함
    assert response.status_code == 403

def test_get_vehicle_list_empty(client, session, admin_token):
    # GIVEN: 차량 테이블을 초기화하여 빈 상태로 만듦
    session.exec(text("DELETE FROM vehicle"))
    session.commit()

    # WHEN: 관리자 토큰으로 빈 차량 목록 조회 요청
    response = client.get(
        "/admin/vehicles?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # THEN: 응답 결과는 빈 리스트이어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    vehicles = data["data"]["vehicles"]
    assert isinstance(vehicles, list)
    assert len(vehicles) == 0

def test_get_vehicle_list_pagination(client, session, create_dummy_vehicles, admin_token, clear_vehicles):
    # GIVEN: 차량 테이블 초기화 후 5개의 더미 차량 생성
    clear_vehicles()  # clear_vehicles fixture를 통해 DB 초기화
    create_dummy_vehicles(5)

    # WHEN: 페이지 사이즈 3으로 각 페이지 요청 (page1, page2, page3)
    response1 = client.get(
        "/admin/vehicles?page=1&pageSize=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    response2 = client.get(
        "/admin/vehicles?page=2&pageSize=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    response3 = client.get(
        "/admin/vehicles?page=3&pageSize=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # THEN: page1은 3개, page2는 2개, page3는 빈 리스트
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert len(data1["data"]["vehicles"]) == 3
    assert len(data2["data"]["vehicles"]) == 2
    assert len(data3["data"]["vehicles"]) == 0

def test_get_vehicle_list_invalid_page(client, admin_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: page 값이 0으로 GET 요청 시
    response = client.get(
        "/admin/vehicles?page=0&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_get_vehicle_list_invalid_page_size(client, admin_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: pageSize 값이 0으로 GET 요청 시
    response = client.get(
        "/admin/vehicles?page=1&pageSize=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_vehicle_field_conversion(client, session, create_dummy_vehicles, admin_token, clear_vehicles):
    # GIVEN: 차량 테이블 초기화 후 단일 차량 데이터 생성
    clear_vehicles()
    create_dummy_vehicles(1)

    # WHEN: 관리자 토큰으로 단일 차량 조회 GET 요청 수행
    response = client.get(
        "/admin/vehicles?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # THEN: current_location이 dict로 변환되고, status가 "active"로 매핑됨
    assert response.status_code == 200
    data = response.json()
    vehicles = data["data"]["vehicles"]
    assert len(vehicles) > 0
    vehicle = vehicles[0]
    loc = vehicle["current_location"]
    assert isinstance(loc, dict)
    assert loc["x"] == 12.313
    assert loc["y"] == 32.3232
    assert vehicle["item_status_name"] == "active"
