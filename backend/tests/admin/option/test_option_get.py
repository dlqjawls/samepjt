import pytest
from datetime import datetime
from sqlmodel import Session
from app.db.models.option import Option
from app.core.jwt import jwt_handler
from sqlalchemy import text
import json

from app.utils.lut_constants import ItemStatus

# GIVEN: 관리자 토큰 생성 (role "master")
@pytest.fixture
def admin_token():
    return jwt_handler.create_token(1, role="master")[0]

# GIVEN: 비관리자 토큰 생성 (role "user")
@pytest.fixture
def non_admin_token():
    return jwt_handler.create_token(2, role="user")[0]

# GIVEN: 옵션 테이블 초기화 헬퍼
@pytest.fixture
def clear_options(session: Session):
    def _clear():
        session.exec(text("DELETE FROM option"))
        session.commit()
    return _clear

# GIVEN: 더미 옵션 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_options(session: Session):
    def _create(count: int = 3):
        options = []
        for i in range(count):
            # JSON 형식의 좌표 문자열 생성
            option = Option(
                option_type_id=1,
                item_status_id=ItemStatus.ACTIVE,
                created_by=1,
                updated_by=1
            )
            session.add(option)
            options.append(option)
        session.commit()
        return options
    return _create

def test_get_option_list_success(client, session, create_dummy_options, admin_token):
    # GIVEN: 관리자 토큰과 3개의 더미 옵션 데이터가 준비됨
    create_dummy_options(3)
    
    # WHEN: /admin/options 엔드포인트를 GET 요청
    response = client.get(
        "/admin/options?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # THEN: 응답이 성공적이고, 각 옵션 필드가 올바르게 매핑됨
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "options" in data["data"]
    options = data["data"]["options"]
    assert isinstance(options, list)
    assert len(options) >= 3
    
    # 첫 번째 옵션 데이터 검증
    option = options[0]
    assert "option_id" in option
    assert "option_type_id" in option
    assert "item_status_name" in option
    assert "created_at" in option
    assert "created_by" in option
    assert "updated_at" in option
    assert "updated_by" in option

def test_get_option_list_unauthorized(client):
    # 인증 토큰 없이 호출 시 401 Unauthorized 반환 확인
    response = client.get("/admin/options?page=1&pageSize=10")
    assert response.status_code == 401

def test_get_option_list_non_admin(client, session, create_dummy_options, non_admin_token):
    # GIVEN: 비관리자 토큰과 3개의 더미 옵션 데이터가 준비됨
    create_dummy_options(3)

    # WHEN: /admin/options 엔드포인트를 비관리자 토큰으로 호출
    response = client.get(
        "/admin/options?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    # THEN: 403 Forbidden 응답이 발생함
    assert response.status_code == 403

def test_get_option_list_empty(client, session, admin_token):
    # GIVEN: 옵션 테이블을 초기화하여 빈 상태로 만듦
    session.exec(text("DELETE FROM option"))
    session.commit()

    # WHEN: 관리자 토큰으로 빈 옵션 목록 조회 요청
    response = client.get(
        "/admin/options?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # THEN: 응답 결과는 빈 리스트이어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    options = data["data"]["options"]
    assert isinstance(options, list)
    assert len(options) == 0

def test_get_option_list_pagination(client, session, create_dummy_options, admin_token, clear_options):
    # GIVEN: 옵션 테이블 초기화 후 5개의 더미 옵션 생성
    clear_options()  # clear_options fixture를 통해 DB 초기화
    create_dummy_options(5)

    # WHEN: 페이지 사이즈 3으로 각 페이지 요청 (page1, page2, page3)
    response1 = client.get(
        "/admin/options?page=1&pageSize=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    response2 = client.get(
        "/admin/options?page=2&pageSize=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    response3 = client.get(
        "/admin/options?page=3&pageSize=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # THEN: page1은 3개, page2는 2개, page3는 빈 리스트
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert len(data1["data"]["options"]) == 3
    assert len(data2["data"]["options"]) == 2
    assert len(data3["data"]["options"]) == 0

def test_get_option_list_invalid_page(client, admin_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: page 값이 0으로 GET 요청 시
    response = client.get(
        "/admin/options?page=0&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_get_option_list_invalid_page_size(client, admin_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: pageSize 값이 0으로 GET 요청 시
    response = client.get(
        "/admin/options?page=1&pageSize=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_option_field_conversion(client, session, create_dummy_options, admin_token, clear_options):
    # GIVEN: 옵션 테이블 초기화 후 단일 옵션 데이터 생성
    clear_options()
    create_dummy_options(1)

    # WHEN: 관리자 토큰으로 단일 옵션 조회 GET 요청 수행
    response = client.get(
        "/admin/options?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # THEN: current_location이 dict로 변환되고, status가 "active"로 매핑됨
    assert response.status_code == 200
    data = response.json()
    options = data["data"]["options"]
    assert len(options) > 0
    option = options[0]
    # loc = module["current_location"]
    # assert isinstance(loc, dict)
    # assert loc["x"] == 12.313
    # assert loc["y"] == 32.3232
    assert option["item_status_name"] == "active"
