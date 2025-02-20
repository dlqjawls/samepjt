import pytest
from sqlmodel import Session, select
from app.db.models.option import Option
from app.db.models.option_type import OptionType
from app.utils.lut_constants import ItemStatus
from tests.helpers import master_token, user_token, create_dummy_options


@pytest.fixture
def first_three_option_type_ids(session: Session):
    option_types = session.exec(select(OptionType)).all()
    # 조건에 맞게 첫 3개의 id를 선정 (존재 여부 검증 필요)
    return [ot.option_type_id for ot in option_types][:3]

def test_create_option_success(client, session, master_token, first_three_option_type_ids):
    """정상적인 옵션 등록 테스트"""
    option_data = {
        "option_type_id": first_three_option_type_ids[0],
    }
    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option registered successfully"
    
    stmt = select(Option).where(Option.option_type_id == option_data["option_type_id"])
    registered_option = session.exec(stmt).first()
    assert registered_option is not None
    assert registered_option.option_type_id == option_data["option_type_id"]
    assert registered_option.item_status_id == ItemStatus.INACTIVE.ID

def test_create_option_unauthorized(client, first_three_option_type_ids):
    """인증 없이 옵션 등록 시도"""
    option_data = {
        "option_type_id": first_three_option_type_ids[0],
    }
    response = client.post(
        "/api/admin/options",
        json=option_data
    )
    assert response.status_code == 401

def test_create_option_forbidden(client, user_token, first_three_option_type_ids):
    """권한 없는 사용자의 옵션 등록 시도"""    
    option_data = {
        "option_type_id": first_three_option_type_ids[0],
    }
    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

@pytest.mark.parametrize("invalid_option_type_id", [
    "0", 
    "-1",
    "a",
    "abc",
    "1.5",
    "*"
])
def test_create_option_invalid_option_type_id_format(client, master_token, invalid_option_type_id):
    """잘못된 옵션 타입 형식으로 등록 시도"""
    option_data = {
        "option_type_id": invalid_option_type_id,
    }
    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"
    
@pytest.mark.parametrize("non_existent_option_type_id", [
    "99999",
    "100000",
])
def test_create_option_non_existent_option_type_id(client, master_token, non_existent_option_type_id):
    """존재하지 않는 옵션 타입 형식으로 등록 시도"""
    option_data = {
        "option_type_id": non_existent_option_type_id,
    } 
    response = client.post(
        "/api/admin/options",
        json=option_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 404
    assert response.json()["resultCode"] == "FAILURE"   

@pytest.mark.parametrize("missing_field", [
    {}
])
def test_create_option_missing_fields(client, master_token, missing_field):
    """필수 필드 누락 테스트"""
    response = client.post(
        "/api/admin/options",
        json=missing_field,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"

def test_create_multiple_options_success(client, session, master_token, first_three_option_type_ids):
    """여러 옵션 연속 등록 테스트"""
    options_data = [
        {"option_type_id": first_three_option_type_ids[i]}
        for i in range(3)
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


def test_create_multiple_options_success2(client, session, master_token, first_three_option_type_ids):
    """한 옵션 타입 연속 등록 테스트"""
    options_data = [
        {"option_type_id": first_three_option_type_ids[0]}
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
