import pytest
from datetime import datetime
from app.db.models.option_type import OptionType
from sqlmodel import Session, select

from tests.helpers import master_token, semi_admin_token

@pytest.fixture
def test_option_type(session: Session):
    """테스트용 옵션 타입 데이터 생성"""
    option_type = OptionType(
        option_type_name="Test Option Type",
        option_type_size="1x1",
        option_type_cost=10000,
        description="Test Description",
        option_type_images="",
        option_type_features="Feature1, Feature2",
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(option_type)
    session.commit()
    session.refresh(option_type)
    return option_type

def get_option_type_id(session: Session, option_type_name: str) -> int:
    """옵션 타입 ID 조회"""
    option_type = session.exec(select(OptionType).where(OptionType.option_type_name == option_type_name)).first()
    if option_type is None or option_type.option_type_id is None:
        raise ValueError(f"Option type with name {option_type_name} not found")
    return option_type.option_type_id


def test_update_option_type_success(client, session, master_token, test_option_type):
    """정상적인 옵션 타입 정보 업데이트 테스트"""
    
    # Given: 옵션 타입 정보 업데이트 요청 데이터
    update_data = {
        "option_type_name": "Updated Option Type",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "description": "Updated Description",
        "option_type_features": "Updated Feature1, Updated Feature2"
    }
    # When: 마스터 권한으로 옵션 타입 정보 업데이트 요청
    response = client.patch(
        f"/api/admin/option-types/{get_option_type_id(session, test_option_type.option_type_name)}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option type updated successfully"

    # Then: DB에 저장된 데이터 검증
    updated_option_type = session.exec(
        select(OptionType).where(OptionType.option_type_id == get_option_type_id(session, test_option_type.option_type_name))
    ).first()
    assert updated_option_type.option_type_name is not None
    assert updated_option_type.description is not None
    assert updated_option_type.option_type_features is not None
    assert updated_option_type.option_type_size is not None

def test_update_option_type_unauthorized(client, session, test_option_type, semi_admin_token):
    """❌ 권한 없는 사용자의 옵션 타입 정보 업데이트 시도"""  
    update_data = {
        "option_type_name": "Updated Option Type",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "description": "Updated Description",
        "option_type_features": "Updated Feature1, Updated Feature2"
    }

    response = client.patch(
        f"/api/admin/option-types/{get_option_type_id(session, test_option_type.option_type_name)}",
        json=update_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Permission denied" in data["message"]

def test_update_nonexistent_option_type(client, session, master_token):
    """❌ 존재하지 않는 옵션 타입 정보 업데이트 시도"""
    update_data = {
        "option_type_name": "Updated Option Type",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "description": "Updated Description",
        "option_type_features": "Updated Feature1, Updated Feature2"
    }

    response = client.patch(
        "/api/admin/option-types/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Option type not found" in data["message"]


def test_update_option_type_without_token(client, session, test_option_type):
    """❌ 인증 토큰 없이 옵션 타입 정보 업데이트 시도"""
    update_data = {
        "option_type_name": "Updated Option Type",
        "option_type_size": "1x1",
        "option_type_cost": 10000,
        "description": "Updated Description",
        "option_type_features": "Updated Feature1, Updated Feature2"
    }

    response = client.patch(
        f"/api/admin/option-types/{get_option_type_id(session, test_option_type.option_type_name)}",
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Authentication" in data["message"]

