import pytest
from sqlmodel import Session, select
from app.db.models.module import Module
from app.utils.lut_constants import ItemStatus, ModuleType
from tests.helpers import master_token, user_token, create_dummy_modules


@pytest.mark.parametrize("module_type_id", [
    ModuleType.MEDIUM.ID,
    ModuleType.SMALL.ID,
    ModuleType.LARGE.ID,
])
def test_create_module_success(client, session, master_token, module_type_id):
    """정상적인 모듈 등록 테스트"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": module_type_id,
    }
    response = client.post(
        "/api/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module registered successfully"
    
    stmt = select(Module).where(Module.module_nfc_tag_id == module_data["module_nfc_tag_id"])
    registered_module = session.exec(stmt).first()
    assert registered_module is not None
    assert registered_module.module_type_id == module_data["module_type_id"]
    assert registered_module.item_status_id == ItemStatus.INACTIVE.ID

def test_create_module_unauthorized(client):
    """인증 없이 모듈 등록 시도"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": ModuleType.MEDIUM.ID,
    }
    response = client.post(
        "/api/admin/modules",
        json=module_data
    )
    assert response.status_code == 401

def test_create_module_forbidden(client, user_token):
    """권한 없는 사용자의 모듈 등록 시도"""    
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": ModuleType.MEDIUM.ID,
    }
    response = client.post(
        "/api/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    
def test_create_module_duplicate_module_nfc_tag_id(client, session, master_token, create_dummy_modules):
    """중복된 모듈 NFC 태그 ID로 모듈 등록 시도"""
    modules = create_dummy_modules(1)
    module = modules[0]
    duplicate_data = {
        "module_nfc_tag_id": module.module_nfc_tag_id,
        "module_type_id": ModuleType.MEDIUM.ID,
    }
    response = client.post(
        "/api/admin/modules",
        json=duplicate_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"].lower()
  

@pytest.mark.parametrize("invalid_module_nfc_tag_id", [
    "",  # 빈 문자열
    "TEST@123",  # 특수문자 포함
    "TEST 123",  # 공백 포함
    "TEST-123",  # 하이픈 포함
    "TEST_123",  # 언더스코어 포함
    "1A1FF1043",  # 14자리 미만
    "1A1FF1043E2BC61",  # 15자리 초과
])
def test_create_module_invalid_module_nfc_tag_id_format(client, master_token, invalid_module_nfc_tag_id):
    """잘못된 모듈 NFC 태그 ID 형식으로 등록 시도"""
    module_data = {
        "module_nfc_tag_id": invalid_module_nfc_tag_id,
        "module_type_id": ModuleType.MEDIUM.ID,
    }
    response = client.post(
        "/api/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

@pytest.mark.parametrize("invalid_module_type_id", [
    "0", 
    "-1",
    "a",
    "abc",
    "1.5",
    "*"
])
def test_create_module_invalid_module_type_id_format(client, master_token, invalid_module_type_id):
    """잘못된 모듈 타입 형식으로 등록 시도"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": invalid_module_type_id,
    }
    response = client.post(
        "/api/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"
    
@pytest.mark.parametrize("non_existent_module_type_id", [
    "99999",
    "100000",
])
def test_create_module_non_existent_module_type_id(client, master_token, non_existent_module_type_id):
    """존재하지 않는 모듈 타입 형식으로 등록 시도"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": non_existent_module_type_id,
    } 
    response = client.post(
        "/api/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 404
    assert response.json()["resultCode"] == "FAILURE"   

@pytest.mark.parametrize("missing_field", [
    {"module_nfc_tag_id": "1A1FF1043E2BC6"},
    {"module_type_id": ModuleType.MEDIUM.ID},
    {}
])
def test_create_module_missing_fields(client, master_token, missing_field):
    """필수 필드 누락 테스트"""
    response = client.post(
        "/api/admin/modules",
        json=missing_field,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"

@pytest.mark.parametrize("module_type_id,nfc_tag_id", [
    (ModuleType.MEDIUM.ID, "1A1FF1043E2BC"),
    (ModuleType.SMALL.ID, "2A1FF1043E2BC"),
    (ModuleType.LARGE.ID, "3A1FF1043E2BC"),
])
def test_create_multiple_modules_success(client, session, master_token, module_type_id, nfc_tag_id):
    """여러 모듈 연속 등록 테스트"""
    modules_data = [
        {"module_nfc_tag_id": f"{nfc_tag_id}{i}", "module_type_id": module_type_id}
        for i in range(1, 4)
    ]

    for module_data in modules_data:
        response = client.post(
            "/admin/modules",
            json=module_data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["resultCode"] == "SUCCESS"

    # DB에 모든 모듈이 저장되었는지 확인
    for module_data in modules_data:
        module = session.exec(
            select(Module).where(Module.module_nfc_tag_id == module_data["module_nfc_tag_id"])
        ).first()
        assert module is not None
        assert module.module_nfc_tag_id == module_data["module_nfc_tag_id"]
