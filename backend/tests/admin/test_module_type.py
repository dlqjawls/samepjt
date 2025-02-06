import pytest
from fastapi.testclient import TestClient
from app.core.jwt import jwt_handler

# 관리자 권한 토큰 (role: master)
def get_admin_token() -> str:
    token, _ = jwt_handler.create_token(1, role="master")
    return token

# 사용자 권한 토큰 (role: user) - 관리자 API 접근 불가
def get_user_token() -> str:
    token, _ = jwt_handler.create_token(2, role="user")
    return token

def test_get_module_types_success(client: TestClient):
    headers = {"Authorization": f"Bearer {get_admin_token()}"}
    response = client.get("/admin/module-types", headers=headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert data["resultCode"] == "SUCCESS", f"Unexpected resultCode: {data.get('resultCode')}"
    assert "data" in data, "Response missing 'data' field"
    assert "module_types" in data["data"], "Response data missing 'module_types'"
    assert isinstance(data["data"]["module_types"], list), "'module_types' should be a list"

def test_get_module_types_unauthorized(client: TestClient):
    # 토큰 없이 요청 시
    response = client.get("/admin/module-types")
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

def test_get_module_types_forbidden(client: TestClient):
    # 사용자 토큰은 관리자 API 접근이 불가해야 함 
    headers = {"Authorization": f"Bearer {get_user_token()}"}
    response = client.get("/admin/module-types", headers=headers)
    # 인증은 되었지만 권한 부족인 경우 보통 403 혹은 401
    assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"

def test_get_module_types_empty(client: TestClient, monkeypatch):
    """
    모듈 타입이 DB에 존재하지 않을 경우(빈 리스트)에도
    정상적인 SUCCESS 응답과 빈 리스트를 반환하는지 검증합니다.
    """
    from app.api.schemas.admin.module_type_schema import ModuleTypesData, ModuleTypesResponse
    from app.services.admin.module_type_service import ModuleTypeService
    
    def fake_get_all_module_types(session):
        return ModuleTypesResponse(
            resultCode="SUCCESS",
            message="Module types retrieved successfully",
            data=ModuleTypesData(module_types=[])
        )

    monkeypatch.setattr(ModuleTypeService, "get_all_module_types", fake_get_all_module_types)

    headers = {"Authorization": f"Bearer {get_admin_token()}"}
    response = client.get("/admin/module-types", headers=headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert data["resultCode"] == "SUCCESS", f"Unexpected resultCode: {data.get('resultCode')}"
    assert "data" in data, "Response missing 'data' field"
    assert "module_types" in data["data"], "Response data missing 'module_types'"
    assert data["data"]["module_types"] == [], "Expected empty module_types list" 