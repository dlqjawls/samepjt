import pytest
from sqlmodel import SQLModel

def test_get_module_sets_success(client):
    """✅ 정상적인 모듈 세트 목록 조회 테스트"""
    
    # Given: 서버에 기본 데이터가 있는 상태
    response = client.get("/api/user/module-sets?page=1&page_size=10")

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "moduleSets" in data["data"]
    assert isinstance(data["data"]["moduleSets"], list)

def test_get_module_sets_not_found(client, session):
    """🛑 모듈 세트가 없을 경우 빈 리스트 반환 테스트 (404 → 200으로 수정)"""
    
    # Given: DB를 초기화하여 모듈 세트 데이터가 없는 상태
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.exec(table.delete())
    session.commit()

    # When: 모듈 세트 조회 요청
    response = client.get("/api/user/module-sets?page=1&page_size=10")

    # Then: 200 OK + 빈 리스트 응답 검증 (API가 빈 리스트 반환하는 경우)
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert isinstance(data["data"]["moduleSets"], list)
    assert len(data["data"]["moduleSets"]) == 0  # ✅ 빈 리스트 체크

def test_get_module_sets_invalid_page(client):
    """🚨 유효하지 않은 페이지 번호 요청 테스트"""

    # When: `page=0` (잘못된 값)으로 요청
    response = client.get("/api/user/module-sets?page=0&page_size=10")

    # Then: 422 응답 검증
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation" in data["message"].lower()

def test_get_module_sets_invalid_page_size(client):
    """🚨 유효하지 않은 페이지 크기 요청 테스트"""

    # When: `page_size=0` (잘못된 값)으로 요청
    response = client.get("/api/user/module-sets?page=1&page_size=0")

    # Then: 422 응답 검증
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation" in data["message"].lower()

def test_get_module_sets_large_page_number(client):
    """🚨 페이지 번호가 너무 클 때 빈 리스트 반환 테스트 (404 → 200으로 수정)"""

    # When: `page=999` (너무 큰 값)으로 요청
    response = client.get("/api/user/module-sets?page=999&page_size=10")

    # Then: 200 OK + 빈 리스트 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert isinstance(data["data"]["moduleSets"], list)
    assert len(data["data"]["moduleSets"]) == 0  # ✅ 빈 리스트 체크

def test_get_module_sets_empty_database(client, session):
    """🛑 모듈 세트 데이터가 없는 경우 빈 리스트 반환 테스트 (404 → 200으로 수정)"""

    # Given: DB를 초기화하여 모듈 세트 데이터가 없는 상태
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.exec(table.delete())
    session.commit()

    # When: 모듈 세트 조회 요청
    response = client.get("/api/user/module-sets?page=1&page_size=10")

    # Then: 200 OK + 빈 리스트 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert isinstance(data["data"]["moduleSets"], list)
    assert len(data["data"]["moduleSets"]) == 0  # ✅ 빈 리스트 체크
