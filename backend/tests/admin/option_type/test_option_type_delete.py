import pytest
from sqlmodel import Session, select
from app.db.models.option_type import OptionType
from datetime import datetime

from tests.helpers import master_token, semi_admin_token

@pytest.fixture
def test_option_type(session: Session):
    """테스트용 옵션 타입 데이터 생성"""
    option_type = OptionType(
        option_type_name="Test Option Type",
        option_type_size=500,
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
    option_type = session.exec(
        select(OptionType).where(OptionType.option_type_name == option_type_name)
    ).first()
    if not option_type or option_type.option_type_id is None:
        raise ValueError(f"Option type with name '{option_type_name}' not found")
    return option_type.option_type_id

def test_delete_option_type_success(client, session, master_token, test_option_type):
    """✅ 옵션 타입 삭제 성공 테스트"""
    option_type_id = get_option_type_id(session, test_option_type.option_type_name)
    
    # DELETE 요청
    response = client.delete(
        f"/api/admin/option-types/{option_type_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200, (
        f"Expected status code 200, got {response.status_code}. Response: {response.json()}"
    )
    data = response.json()
    assert data["resultCode"] == "SUCCESS", f"Unexpected resultCode: {data}"
    assert data["message"] == "Option type deleted successfully", f"Unexpected message: {data}"
    
    # 같은 ID로 재삭제 시도 -> 존재하지 않으므로 404
    response2 = client.delete(
        f"/api/admin/option-types/{option_type_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response2.status_code == 404, (
        f"Expected status code 404 on re-deletion, got {response2.status_code}. Response: {response2.json()}"
    )

def test_delete_option_type_not_found(client, master_token):
    """❌ 존재하지 않는 옵션 타입 삭제 시도 테스트"""
    response = client.delete(
        "/admin/option-types/99999",  # 존재하지 않는 ID 사용
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 404, (
        f"Expected status code 404, got {response.status_code}. Response: {response.json()}"
    )
    data = response.json()
    assert data["resultCode"] == "FAILURE", f"Unexpected resultCode: {data}"
    assert "not found" in data["message"].lower(), f"Unexpected message: {data}"

def test_delete_option_type_without_token(client, session, test_option_type):
    """❌ 인증 토큰 없이 옵션 타입 삭제 시도 테스트"""
    option_type_id = get_option_type_id(session, test_option_type.option_type_name)
    response = client.delete(f"/admin/option-types/{option_type_id}")
    assert response.status_code == 401, (
        f"Expected status code 401, got {response.status_code}. Response: {response.json()}"
    )
    data = response.json()
    assert data["resultCode"] == "FAILURE", f"Unexpected resultCode: {data}"
    assert "authentication" in data["message"].lower(), f"Unexpected message: {data}"

def test_delete_option_type_with_non_master_token(client, session, test_option_type, semi_admin_token):
    """❌ 권한 없는 사용자의 옵션 타입 삭제 시도 테스트"""
    option_type_id = get_option_type_id(session, test_option_type.option_type_name)
    response = client.delete(
        f"/api/admin/option-types/{option_type_id}",
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403, (
        f"Expected status code 403, got {response.status_code}. Response: {response.json()}"
    )
    data = response.json()
    assert data["resultCode"] == "FAILURE", f"Unexpected resultCode: {data}"
    assert "permission" in data["message"].lower(), f"Unexpected message: {data}"
