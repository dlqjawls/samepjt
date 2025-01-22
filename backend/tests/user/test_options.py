import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)  # FastAPI 애플리케이션 클라이언트 생성

def test_get_options_success():
    """
    (Success) 정상적인 옵션 목록 조회 테스트

    Given: 옵션 데이터가 존재할 때
    When: 기본 페이지(page=1)와 페이지 크기(page_size=5)로 요청하면
    Then: 응답 상태 코드 200과 "SUCCESS" 메시지를 반환하고, 데이터가 포함되어 있어야 한다.
    """
    response = client.get("/user/options?page=1&page_size=5")

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Options retrieved successfully"
    assert "options" in json_response["data"]
    assert len(json_response["data"]["options"]) > 0  # 최소 한 개의 데이터 존재 확인


def test_get_options_search_from_module_sets():
    """
    (Success) 모듈 세트에서 옵션 검색 테스트

    Given: 모듈 리스트가 존재하고 최소 하나의 모듈에 옵션이 있을 때
    When: 옵션이 포함된 첫 번째 모듈의 첫 번째 옵션 ID를 검색하면
    Then: 응답 상태 코드 200과 해당 옵션이 포함된 결과를 반환해야 한다.
    """

    # 모듈 리스트를 가져옴
    module_response = client.get("/user/module-sets?page=1&page_size=5")
    assert module_response.status_code == 200
    module_data = module_response.json()

    # 옵션이 포함된 첫 번째 모듈을 찾을 때까지 반복
    option_id = None

    for module_set in module_data["data"]["moduleSets"]:
        if module_set.get("suppliedOptions"):  # 옵션이 존재하는 모듈 찾기
            option_id = module_set["suppliedOptions"][0]["optionId"]
            break  # 첫 번째 옵션이 있는 모듈을 찾으면 종료

    # 옵션이 없는 경우 테스트 건너뛰기
    if not option_id:
        pytest.skip("검색할 옵션이 포함된 모듈 세트를 찾을 수 없어 테스트를 건너뜁니다.")

    # 옵션 검색 API를 호출하여 확인 (옵션 ID로 검색)
    response = client.get(f"/user/options?option_id={option_id}")
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Options retrieved successfully"
    assert any(option["optionId"] == option_id for option in json_response["data"]["options"])


def test_get_options_no_data():
    """
    (Success) 옵션 데이터가 없을 때

    Given: 존재하지 않는 옵션 ID (9999)를 입력할 때
    When: 해당 ID로 조회하면
    Then: 응답 상태 코드 200과 빈 목록을 반환해야 한다.
    """
    response = client.get("/user/options?option_id=9999")

    json_response = response.json()
    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Options retrieved successfully"
    assert "options" in json_response["data"]
    assert len(json_response["data"]["options"]) == 0  # 데이터가 비어 있음을 확인


def test_get_options_invalid_page_size():
    """
    (Fail) page_size가 0이거나 음수일 때

    Given: page_size가 0 또는 음수일 때
    When: 조회 요청을 보내면
    Then: 응답 상태 코드 422와 "ensure this value is greater than 0" 메시지를 반환해야 한다.
    """
    response = client.get("/user/options?page=1&page_size=0")

    json_response = response.json()
    assert response.status_code == 422  # FastAPI의 데이터 검증 오류
    assert json_response["detail"][0]["msg"] == "ensure this value is greater than 0"


def test_get_options_invalid_page():
    """
    (Fail) page 값이 0이거나 음수일 때

    Given: page 값이 0 또는 음수일 때
    When: 조회 요청을 보내면
    Then: 응답 상태 코드 422와 "ensure this value is greater than 0" 메시지를 반환해야 한다.
    """
    response = client.get("/user/options?page=0&page_size=5")

    json_response = response.json()
    assert response.status_code == 422  # FastAPI의 데이터 검증 오류
    assert json_response["detail"][0]["msg"] == "ensure this value is greater than 0"


def test_get_options_missing_query_params():
    """
    (Success) 쿼리 파라미터가 누락된 경우 기본값으로 정상 처리

    Given: page 또는 page_size를 전달하지 않을 때
    When: 기본값으로 요청이 처리되면
    Then: 응답 상태 코드 200과 기본 페이지 크기(10개)로 응답해야 한다.
    """
    response = client.get("/user/options")

    json_response = response.json()
    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Options retrieved successfully"
    assert "options" in json_response["data"]
    assert len(json_response["data"]["options"]) > 0
