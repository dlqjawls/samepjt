import pytest
from sqlmodel import Session
from app.db.models.module_set import ModuleSet
from sqlalchemy import text

from tests.helpers import master_token, user_token

# GIVEN: 모듈 세트 테이블 초기화 헬퍼
@pytest.fixture
def clear_module_sets(session: Session):
    def _clear():
        session.exec(text("DELETE FROM module_set"))
        session.commit()
    return _clear

# GIVEN: 더미 모듈 세트 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_module_sets(session: Session):
    def _create(count: int = 3):
        module_sets = []
        for i in range(count):
            module_set = ModuleSet(
                module_set_name=f"MODULE_SET{i+1}",
                description=f"DESCRIPTION{i+1}",
                module_set_images=f"IMAGE{i+1}",
                module_set_features=f"FEATURES{i+1}",
                module_type_id=1,
                created_by=1,
                updated_by=1
            )
            session.add(module_set)
            module_sets.append(module_set)
        session.commit()
        return module_sets
    return _create

def test_get_module_set_list_success(client, session, create_dummy_module_sets, master_token):
    # GIVEN: 관리자 토큰과 3개의 더미 모듈 세트 데이터가 준비됨
    create_dummy_module_sets(3)
    
    # WHEN: /admin/module-sets 엔드포인트를 GET 요청
    response = client.get(
        "/api/admin/module-sets?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    
    # THEN: 응답이 성공적이고, 각 모듈 세트 필드가 올바르게 매핑됨
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "module_sets" in data["data"]
    module_sets = data["data"]["module_sets"]
    assert isinstance(module_sets, list)
    assert len(module_sets) >= 3
    
    # 첫 번째 모듈 세트 데이터 검증
    module_set = module_sets[0]
    assert "module_set_id" in module_set
    assert "module_set_name" in module_set
    assert "description" in module_set
    assert "module_set_images" in module_set
    assert "module_set_features" in module_set
    assert "module_type_id" in module_set
    assert "cost" in module_set
    assert "created_at" in module_set
    assert "created_by" in module_set
    assert "updated_at" in module_set
    assert "updated_by" in module_set

def test_get_module_set_list_unauthorized(client):
    # 인증 토큰 없이 호출 시 401 Unauthorized 반환 확인
    response = client.get("/api/admin/module-sets?page=1&pageSize=10")
    assert response.status_code == 401

def test_get_module_set_list_non_admin(client, session, create_dummy_module_sets, user_token):
    # GIVEN: 비관리자 토큰과 3개의 더미 모듈 세트 데이터가 준비됨
    create_dummy_module_sets(3)

    # WHEN: /admin/module-sets 엔드포인트를 비관리자 토큰으로 호출
    response = client.get(
        "/api/admin/module-sets?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # THEN: 403 Forbidden 응답이 발생함
    assert response.status_code == 403

def test_get_module_set_list_empty(client, session, master_token):
    # GIVEN: 모듈 세트 테이블을 초기화하여 빈 상태로 만듦
    session.exec(text("DELETE FROM module_set"))
    session.commit()

    # WHEN: 관리자 토큰으로 빈 모듈 세트 목록 조회 요청
    response = client.get(
        "/api/admin/module-sets?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 응답 결과는 빈 리스트이어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    module_sets = data["data"]["module_sets"]
    assert isinstance(module_sets, list)
    assert len(module_sets) == 0

def test_get_module_set_list_pagination(client, session, create_dummy_module_sets, master_token, clear_module_sets):
    # GIVEN: 모듈 세트 테이블 초기화 후 5개의 더미 모듈 세트 생성
    clear_module_sets()  # clear_module_sets fixture를 통해 DB 초기화
    create_dummy_module_sets(5)

    # WHEN: 페이지 사이즈 3으로 각 페이지 요청 (page1, page2, page3)
    response1 = client.get(
        "/api/admin/module-sets?page=1&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response2 = client.get(
        "/api/admin/module-sets?page=2&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response3 = client.get(
        "/api/admin/module-sets?page=3&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: page1은 3개, page2는 2개, page3는 빈 리스트
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert len(data1["data"]["module_sets"]) == 3
    assert len(data2["data"]["module_sets"]) == 2
    assert len(data3["data"]["module_sets"]) == 0

def test_get_module_set_list_invalid_page(client, master_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: page 값이 0으로 GET 요청 시
    response = client.get(
        "/api/admin/module-sets?page=0&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_get_module_set_list_invalid_page_size(client, master_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: pageSize 값이 0으로 GET 요청 시
    response = client.get(
        "/api/admin/module-sets?page=1&pageSize=0",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_module_set_field_conversion(client, session, create_dummy_module_sets, master_token, clear_module_sets):
    # GIVEN: 모듈 세트 테이블 초기화 후 단일 모듈 세트 데이터 생성
    clear_module_sets()
    create_dummy_module_sets(1)

    # WHEN: 관리자 토큰으로 단일 모듈 세트 조회 GET 요청 수행
    response = client.get(
        "/api/admin/module-sets?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: current_location이 dict로 변환되고, status가 "active"로 매핑됨
    assert response.status_code == 200
    data = response.json()
    module_sets = data["data"]["module_sets"]
    assert len(module_sets) > 0
    module_set = module_sets[0]
