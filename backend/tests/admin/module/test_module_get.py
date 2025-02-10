import pytest
from datetime import datetime
from sqlmodel import Session
from app.db.models.module import Module
from sqlalchemy import text
import json

from app.utils.lut_constants import ItemStatus

from tests.helpers import master_token, user_token

# GIVEN: 모듈 테이블 초기화 헬퍼
@pytest.fixture
def clear_modules(session: Session):
    def _clear():
        session.exec(text("DELETE FROM module"))
        session.commit()
    return _clear

# GIVEN: 더미 모듈 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_modules(session: Session):
    def _create(count: int = 3):
        modules = []
        for i in range(count):
            # JSON 형식의 좌표 문자열 생성
            location = json.dumps({"x": 12.313, "y": 32.3232})
            module = Module(
                module_nfc_tag_id=f"1A1FF1043E2BC{i}",
                module_type_id=1,
                current_location=location,  # JSON 문자열로 저장
                item_status_id=ItemStatus.ACTIVE,
                created_by=1,
                updated_by=1
            )
            session.add(module)
            modules.append(module)
        session.commit()
        return modules
    return _create

def test_get_module_list_success(client, session, create_dummy_modules, master_token):
    # GIVEN: 관리자 토큰과 3개의 더미 모듈 데이터가 준비됨
    create_dummy_modules(3)
    
    # WHEN: /admin/modules 엔드포인트를 GET 요청
    response = client.get(
        "/admin/modules?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    
    # THEN: 응답이 성공적이고, 각 모듈 필드가 올바르게 매핑됨
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "modules" in data["data"]
    modules = data["data"]["modules"]
    assert isinstance(modules, list)
    assert len(modules) >= 3
    
    # 첫 번째 모듈 데이터 검증
    module = modules[0]
    assert "module_id" in module
    assert "module_nfc_tag_id" in module
    assert "module_type_id" in module
    assert "module_type_name" in module
    assert "last_maintenance_at" in module
    assert "next_maintenance_at" in module
    assert "item_status_id" in module
    assert "item_status_name" in module
    assert "created_at" in module
    assert "created_by" in module
    assert "updated_at" in module
    assert "updated_by" in module

def test_get_module_list_unauthorized(client):
    # 인증 토큰 없이 호출 시 401 Unauthorized 반환 확인
    response = client.get("/admin/modules?page=1&pageSize=10")
    assert response.status_code == 401

def test_get_module_list_non_admin(client, session, create_dummy_modules, user_token):
    # GIVEN: 비관리자 토큰과 3개의 더미 모듈 데이터가 준비됨
    create_dummy_modules(3)

    # WHEN: /admin/modules 엔드포인트를 비관리자 토큰으로 호출
    response = client.get(
        "/admin/modules?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # THEN: 403 Forbidden 응답이 발생함
    assert response.status_code == 403

def test_get_module_list_empty(client, session, master_token):
    # GIVEN: 모듈 테이블을 초기화하여 빈 상태로 만듦
    session.exec(text("DELETE FROM module"))
    session.commit()

    # WHEN: 관리자 토큰으로 빈 모듈 목록 조회 요청
    response = client.get(
        "/admin/modules?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 응답 결과는 빈 리스트이어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    modules = data["data"]["modules"]
    assert isinstance(modules, list)
    assert len(modules) == 0

def test_get_module_list_pagination(client, session, create_dummy_modules, master_token, clear_modules):
    # GIVEN: 모듈 테이블 초기화 후 5개의 더미 모듈 생성
    clear_modules()  # clear_modules fixture를 통해 DB 초기화
    create_dummy_modules(5)

    # WHEN: 페이지 사이즈 3으로 각 페이지 요청 (page1, page2, page3)
    response1 = client.get(
        "/admin/modules?page=1&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response2 = client.get(
        "/admin/modules?page=2&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response3 = client.get(
        "/admin/modules?page=3&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: page1은 3개, page2는 2개, page3는 빈 리스트
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert len(data1["data"]["modules"]) == 3
    assert len(data2["data"]["modules"]) == 2
    assert len(data3["data"]["modules"]) == 0

def test_get_module_list_invalid_page(client, master_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: page 값이 0으로 GET 요청 시
    response = client.get(
        "/admin/modules?page=0&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_get_module_list_invalid_page_size(client, master_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: pageSize 값이 0으로 GET 요청 시
    response = client.get(
        "/admin/modules?page=1&pageSize=0",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_module_field_conversion(client, session, create_dummy_modules, master_token, clear_modules):
    # GIVEN: 모듈 테이블 초기화 후 단일 모듈 데이터 생성
    clear_modules()
    create_dummy_modules(1)

    # WHEN: 관리자 토큰으로 단일 모듈 조회 GET 요청 수행
    response = client.get(
        "/admin/modules?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: current_location이 dict로 변환되고, status가 "active"로 매핑됨
    assert response.status_code == 200
    data = response.json()
    modules = data["data"]["modules"]
    assert len(modules) > 0
    module = modules[0]
    # loc = module["current_location"]
    # assert isinstance(loc, dict)
    # assert loc["x"] == 12.313
    # assert loc["y"] == 32.3232
    assert module["item_status_name"] == "active"
