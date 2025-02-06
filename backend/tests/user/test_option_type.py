import pytest
from app.db.models.option_type import OptionType

# 기본 조회 테스트
def test_get_option_types(client):
    response = client.get("user/option-types")
    assert response.status_code == 200
    data = response.json()
    
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option types retrieved successfully"
    assert "optionTypes" in data["data"]
    assert isinstance(data["data"]["optionTypes"], list)
    # 기본 필드 존재 확인
    first_item = data["data"]["optionTypes"][0]
    assert "optionTypeId" in first_item
    assert "optionTypeName" in first_item

# 페이지네이션 테스트
@pytest.mark.parametrize("page,page_size,expected_count", [
    (1, 1, 1),
    (1, 2, 2),
    (2, 1, 1)
])
def test_get_option_types_with_pagination(client, page, page_size, expected_count):
    response = client.get(f"user/option-types?page={page}&page_size={page_size}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["resultCode"] == "SUCCESS"
    assert isinstance(data["data"]["optionTypes"], list)
    assert len(data["data"]["optionTypes"]) <= expected_count  # 마지막 페이지는 더 작을 수 있음

# 잘못된 입력 테스트
@pytest.mark.parametrize("invalid_param", [
    "page=0",
    "page_size=0",
    "page=-1",
    "page_size=-1",
    "page=abc",
    "page_size=abc"
])
def test_get_option_types_invalid_params(client, invalid_param):
    response = client.get(f"user/option-types?{invalid_param}")
    assert response.status_code == 422
    data = response.json()
    
    assert data["resultCode"] == "FAILURE"
    assert data["error_code"] == "VALIDATION_ERROR"

# ID로 조회 테스트
def test_get_option_type_by_id(client, get_first_record_id):
    option_type_id = get_first_record_id(OptionType, "option_type_id")
    
    if option_type_id is None:
        pytest.skip("No option type records found in database")
        
    response = client.get(f"user/option-types/{option_type_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Option type retrieved successfully"
    assert "optionTypes" in data["data"]
    assert isinstance(data["data"]["optionTypes"], list)
    assert len(data["data"]["optionTypes"]) == 1
    # ID 일치 확인
    assert data["data"]["optionTypes"][0]["optionTypeId"] == option_type_id

# 에러 케이스 테스트
@pytest.mark.parametrize("invalid_id,expected_status", [
    ("999", 404),  # 존재하지 않는 ID
    ("invalid", 422),  # 잘못된 형식
    ("0", 422),  # 0
    ("-1", 422),  # 음수
    ("9999999999", 404),  # 매우 큰 수
])
def test_get_option_type_invalid_cases(client, invalid_id, expected_status):
    response = client.get(f"user/option-types/{invalid_id}")
    assert response.status_code == expected_status
    data = response.json()
    
    assert data["resultCode"] == "FAILURE"
    if expected_status == 404:
        assert data["error_code"] == "NOT_FOUND"
    else:
        assert data["error_code"] == "VALIDATION_ERROR"
