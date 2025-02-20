import pytest

from tests.helpers import master_token, semi_admin_token, user_token, create_dummy_modules, create_test_rent

def test_delete_module_success(client, session, master_token, create_dummy_modules):
    """ 모듈 삭제 성공 테스트"""
    modules = create_dummy_modules() 
    response = client.delete(
        f"/api/admin/modules/{modules[0].module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module deleted successfully"

def test_delete_module_not_found(client, master_token):
    """ 존재하지 않는 모듈 삭제 시도 테스트"""
    response = client.delete(
        "/admin/modules/9999",  # 존재하지 않는 ID
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["message"] == "Module not found"
    assert data["error_code"] == "NOT_FOUND"

def test_delete_module_without_token(client, session, create_dummy_modules):
    """ 인증 토큰 없이 모듈 삭제 시도 테스트"""
    modules = create_dummy_modules() 
    response = client.delete(f"/admin/modules/{modules[0].module_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "authentication" in data["message"].lower()

def test_delete_module_with_non_master_token(client, session, create_dummy_modules, semi_admin_token):
    """ 일반 관리자(권한 부족) 토큰으로 모듈 삭제 시도 테스트"""
    modules = create_dummy_modules()  
    response = client.delete(
        f"/api/admin/modules/{modules[0].module_id}",
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "permission denied" in data["message"].lower()

@pytest.mark.parametrize("invalid_module_id", ["abc", -1, 0])
def test_delete_module_invalid_id(client, master_token, invalid_module_id):
    """ 잘못된 형식의 모듈 ID로 삭제 시도 테스트"""
    response = client.delete(
        f"/api/admin/modules/{invalid_module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "value is not a valid integer" in str(data["detail"]).lower() or "validation" in data["message"].lower()

def test_delete_module_already_deleted(client, session, master_token, create_dummy_modules):
    """ 이미 삭제된 모듈 재삭제 시도 테스트"""
    # 첫 번째 삭제 시도 -> 성공 (soft delete)
    modules = create_dummy_modules()
    response_first = client.delete(
        f"/api/admin/modules/{modules[0].module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_first.status_code == 200
    data_first = response_first.json()
    assert data_first["resultCode"] == "SUCCESS"
    
    # 두 번째 삭제 시도 -> 이미 삭제되어 존재하지 않으므로 404 Not Found
    response_second = client.delete(
        f"/api/admin/modules/{modules[0].module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_second.status_code == 404
    data_second = response_second.json()
    assert data_second["resultCode"] == "FAILURE"
    assert data_second["message"] == "Module not found"
    assert data_second["error_code"] == "NOT_FOUND"
