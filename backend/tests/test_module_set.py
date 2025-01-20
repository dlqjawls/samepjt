import pytest

def test_get_module_set_list_success(client):
    """
    ✅ 정상적인 모듈 세트 목록 조회 테스트

    Given: 모듈 세트 데이터가 존재할 때
    When: 기본 페이지(page=1)와 페이지 크기(page_size=5)로 요청을 보내면
    Then: 응답 상태 코드 200과 "SUCCESS" 메시지를 반환하고, 데이터가 포함되어 있어야 한다.
    """
    response = client.get("/user/module-set/list?page=1&page_size=5")

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Module sets retrieved successfully"
    assert "moduleSets" in json_response["data"]
    assert len(json_response["data"]["moduleSets"]) > 0  # 최소 한 개의 데이터 존재 확인


def test_get_module_set_list_no_data(client):
    """
    ❌ 모듈 세트 데이터가 없을 때

    Given: 모듈 세트 데이터가 비어 있을 때
    When: 조회 요청을 보내면
    Then: 응답 상태 코드 404와 "No matching module sets found" 메시지를 반환해야 한다.
    """
    # 더미 데이터가 없도록 설정 
    # TODO:DB 연동 후에는 Mock 처리 필요
    response = client.get("/user/module-set/list?page=100&page_size=5")

    json_response = response.json()

    assert response.status_code == 404
    assert json_response["detail"]["resultCode"] == "FAILURE"
    assert json_response["detail"]["message"] == "No matching module sets found"


def test_get_module_set_list_invalid_page_size(client):
    """
    ❌ page_size가 0이거나 음수일 때

    Given: page_size가 0 또는 음수일 때
    When: 조회 요청을 보내면
    Then: 응답 상태 코드 422와 "ensure this value is greater than 0" 메시지를 반환해야 한다.
    """
    response = client.get("/user/module-set/list?page=1&page_size=0")

    json_response = response.json()

    assert response.status_code == 422  
    assert json_response["detail"][0]["msg"] == "ensure this value is greater than 0" 


def test_get_module_set_list_invalid_page(client):
    """
    ❌ page가 0이거나 음수일 때

    Given: page 값이 0 또는 음수일 때
    When: 조회 요청을 보내면
    Then: 응답 상태 코드 422와 "ensure this value is greater than 0" 메시지를 반환해야 한다.
    """
    response = client.get("/user/module-set/list?page=0&page_size=5")

    json_response = response.json()

    assert response.status_code == 422  
    assert json_response["detail"][0]["msg"] == "ensure this value is greater than 0"  


def test_get_module_set_list_missing_query_params(client):
    """
    ✅ 쿼리 파라미터가 누락된 경우 기본값으로 정상 처리

    Given: page 또는 page_size를 전달하지 않을 때
    When: 기본값으로 요청이 처리되면
    Then: 응답 상태 코드 200과 기본 페이지 크기(10개)로 응답해야 한다.
    """
    response = client.get("/user/module-set/list")

    json_response = response.json()

    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Module sets retrieved successfully"
    assert "moduleSets" in json_response["data"]
    assert len(json_response["data"]["moduleSets"]) > 0
