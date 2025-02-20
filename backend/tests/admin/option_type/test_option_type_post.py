import pytest
from sqlmodel import Session, select, text, delete
from app.db.models.option_type import OptionType
from app.utils.lut_constants import ItemStatus
from faker import Faker

fake = Faker()

from tests.helpers import master_token, semi_admin_token


@pytest.fixture
def clear_option_types(session: Session):
    """옵션 타입 테이블 초기화"""
    session.execute(delete(OptionType))
    session.commit()

def test_create_option_type_success(client, session, master_token, clear_option_types):
    """✅ 정상적인 옵션 타입 등록 테스트"""
    # Given: 옵션 타입 등록 요청 데이터
    option_type_data = {
        "option_type_name": "TEST_OPTION_TYPE",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "option_type_description": "TEST_OPTION_TYPE_DESCRIPTION",
        "option_type_features": "TEST_OPTION_TYPE_FEATURES"
    }

    # When: 마스터 권한으로 옵션 등록 요청
    response = client.post(
        "/api/admin/option-types",
        json=option_type_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option type registered successfully"

    # Then: DB에 저장된 데이터 검증
    option_type = session.exec(select(OptionType).where(OptionType.option_type_name == option_type_data["option_type_name"])).first()
    assert option_type is not None
    assert option_type.option_type_name == option_type_data["option_type_name"]
    assert option_type.option_type_size == option_type_data["option_type_size"]
    assert option_type.option_type_cost == option_type_data["option_type_cost"]


def test_create_option_type_unauthorized(client):
    """❌ 인증 없이 옵션 타입 등록 시도"""
    option_type_data = {
        "option_type_name": "TEST_OPTION_TYPE",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "option_type_description": "TEST_OPTION_TYPE_DESCRIPTION",
        "option_type_features": "TEST_OPTION_TYPE_FEATURES"
    } 
    response = client.post("/api/admin/option-types", json=option_type_data)
    assert response.status_code == 401

def test_create_option_type_forbidden(client, semi_admin_token):
    """❌ 권한 없는 사용자의 옵션 타입 등록 시도"""
    option_type_data = {
        "option_type_name": "TEST_OPTION_TYPE",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "option_type_description": "TEST_OPTION_TYPE_DESCRIPTION",
        "option_type_features": "TEST_OPTION_TYPE_FEATURES"
    }
    response = client.post(
        "/api/admin/option-types",
        json=option_type_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403


@pytest.mark.parametrize("invalid_option_type_data", [
    {"option_type_name": "TEST_OPTION_TYPE"},
    {"option_type_size": "1x1"},
    {"option_type_cost": 10000},
    {"option_type_description": "TEST_OPTION_TYPE_DESCRIPTION"},
    {"option_type_features": "TEST_OPTION_TYPE_FEATURES"},
])
def test_create_option_type_missing_fields(client, master_token, invalid_option_type_data):
    """❌ 필수 필드 누락 테스트"""
    response = client.post(
        "/api/admin/option-types",
        json=invalid_option_type_data,
        headers={"Authorization": f"Bearer {master_token}"}
        )
    
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

def test_create_multiple_option_types_success(client, session, master_token, clear_option_types):
    """✅ 여러 옵션 타입 연속 등록 테스트"""
    option_types_data = [
        {"option_type_name": f"TEST_OPTION_TYPE_{i}",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "option_type_description": "TEST_OPTION_TYPE_DESCRIPTION",
        "option_type_features": "TEST_OPTION_TYPE_FEATURES"}
        for i in range(1, 4)
    ]

    for option_type_data in option_types_data:
        response = client.post(
            "/admin/option-types",
            json=option_type_data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["resultCode"] == "SUCCESS"

    # DB에 모든 옵션이 저장되었는지 확인
    for option_type_data in option_types_data:
        option_type = session.exec(
            select(OptionType).where(OptionType.option_type_name == option_type_data["option_type_name"])
        ).first()
        assert option_type is not None
        assert option_type.option_type_name == option_type_data["option_type_name"]
