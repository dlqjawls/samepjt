import pytest
from datetime import datetime
from app.core.jwt import jwt_handler
from app.db.models.option import Option
from sqlmodel import Session, select
from app.utils.lut_constants import ItemStatus
import json

@pytest.fixture
def master_token():
    """마스터 권한 토큰 생성"""
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    """일반 관리자 권한 토큰 생성"""
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def test_option(session: Session):
    """테스트용 옵션 데이터 생성"""
    option = Option(
        option_type_id=1,
        last_maintenance_at=datetime.now(),
        next_maintenance_at=datetime.now(),
        item_status_id=ItemStatus.ACTIVE,  
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(option)
    session.commit()
    session.refresh(option)
    return option

def test_update_option_success(client, session, master_token, test_option):
    """✅ 정상적인 옵션 정보 업데이트 테스트"""
    # Given: 업데이트할 옵션 데이터
    update_data = {
        "last_maintenance_at": datetime.now().isoformat(),
        "next_maintenance_at": datetime.now().isoformat(),
    }

    # When: 마스터 권한으로 옵션 정보 업데이트 요청
    response = client.patch(
        f"/admin/options/{test_option.option_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option updated successfully"

    # Then: DB에 저장된 데이터 검증
    updated_option = session.exec(
        select(Option).where(Option.option_id == test_option.option_id)
    ).first()
    assert updated_option.last_maintenance_at is not None
    assert updated_option.next_maintenance_at is not None

def test_update_option_unauthorized(client, test_option, semi_admin_token):
    """❌ 권한 없는 사용자의 옵션 정보 업데이트 시도"""
    update_data = {
        "last_maintenance_at": datetime.now().isoformat(),  
        "next_maintenance_at": datetime.now().isoformat(),
    }

    response = client.patch(
        f"/admin/options/{test_option.option_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Permission denied" in data["message"]

def test_update_nonexistent_option(client, master_token):
    """❌ 존재하지 않는 옵션 정보 업데이트 시도"""
    update_data = {
        "last_maintenance_at": datetime.now().isoformat(),
        "next_maintenance_at": datetime.now().isoformat(),
    }

    response = client.patch(
        "/admin/options/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Option not found" in data["message"]


def test_update_option_without_token(client, test_option):
    """❌ 인증 토큰 없이 옵션 정보 업데이트 시도"""
    update_data = {
        "last_maintenance_at": datetime.now().isoformat(),
        "next_maintenance_at": datetime.now().isoformat(),
    }

    response = client.patch(
        f"/admin/options/{test_option.option_id}",
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Authentication" in data["message"]

