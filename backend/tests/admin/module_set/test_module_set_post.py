import pytest
from sqlmodel import Session, select, text, delete
from app.db.models.option import Option
from app.utils.lut_constants import ItemStatus
from faker import Faker

fake = Faker()

from tests.helpers import master_token, semi_admin_token

@pytest.fixture
def clear_options(session: Session):
    """옵션 테이블 초기화"""
    session.execute(delete(Option))
    session.commit()

def test_create_option_success(client, session, master_token, clear_options):
    """✅ 정상적인 옵션 등록 테스트"""
    # Given: 옵션 등록 요청 데이터
    option_data = {
        "option_type_id": 1
    }

    # When: 마스터 권한으로 옵션 등록 요청
    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option registered successfully"

    # Then: DB에 저장된 데이터 검증
    option = session.exec(select(Option).where(Option.option_type_id == option_data["option_type_id"])).first()
    assert option is not None
    assert option.option_type_id == option_data["option_type_id"]
    assert option.item_status_id == ItemStatus.INACTIVE.ID


@pytest.mark.parametrize("invalid_option_type_id", [
    "", # 빈 문자열
    "abc", # 문자열
    "1-1", # 하이픈 포함
])
def test_create_option_invalid_format(client, master_token, invalid_option_type_id):
    """❌ 잘못된 형식의 데이터로 옵션 등록 시도"""
    option_data = {
        "option_type_id": invalid_option_type_id
    }

    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

def test_create_option_unauthorized(client):
    """❌ 인증 없이 옵션 등록 시도"""
    option_data = {
        "option_type_id": 1
    } 
    response = client.post("/api/admin/options", json=option_data)
    assert response.status_code == 401

def test_create_option_forbidden(client, semi_admin_token):
    """❌ 권한 없는 사용자의 옵션 등록 시도"""
    option_data = {
        "option_type_id": 1
    }
    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403


def test_create_option_missing_fields(client, master_token):
    """❌ 필수 필드 누락 테스트"""
    invalid_data_list = [
        {},  # 모든 필드 누락
        {"option_type_id": None},  # option_type_id 누락
    ]

    for data in invalid_data_list:
        response = client.post(
            "/admin/options",
            json=data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 422
        assert response.json()["resultCode"] == "FAILURE"

def test_create_multiple_options_success(client, session, master_token, clear_options):
    """✅ 여러 옵션 연속 등록 테스트"""
    options_data = [
        {"option_type_id": 1}
        for i in range(1, 4)
    ]

    for option_data in options_data:
        response = client.post(
            "/admin/options",
            json=option_data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["resultCode"] == "SUCCESS"

    # DB에 모든 옵션이 저장되었는지 확인
    for option_data in options_data:
        option = session.exec(
            select(Option).where(Option.option_type_id == option_data["option_type_id"])
        ).first()
        assert option is not None
        assert option.option_type_id == option_data["option_type_id"]
