from datetime import datetime
import pytest
from sqlmodel import Session
from app.db.models.option_type import OptionType
from sqlalchemy import text

from tests.helpers import master_token, user_token

# GIVEN: 옵션 타입 테이블 초기화 헬퍼
@pytest.fixture
def clear_option_types(session: Session):
    def _clear():
        session.exec(text("DELETE FROM option_type"))
        session.commit()
    return _clear

# GIVEN: 더미 옵션 타입 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_option_types(session: Session):
    def _create(count: int = 3):
        option_types = []
        for i in range(count):
            option_type = OptionType(
                option_type_name=f"OPTION_TYPE{i+1}",
                option_type_size="1x1",
                option_type_cost=10000,
                description=f"DESCRIPTION{i+1}",
                option_type_images=f"https://www.google.com/image{i+1}",
                option_type_features=f"FEATURES{i+1}",
                created_at=datetime.now(),
                created_by=1,
                updated_at=datetime.now(),
                updated_by=1
            )
            session.add(option_type)
            option_types.append(option_type)
        session.commit()
        return option_types
    return _create

def test_get_option_type_list_success(client, session, clear_option_types, create_dummy_option_types, master_token):
    # GIVEN: 관리자 토큰과 3개의 더미 옵션 타입 데이터가 준비됨
    clear_option_types()
    create_dummy_option_types(3)
    
    # WHEN: /admin/option-types 엔드포인트를 GET 요청
    response = client.get(
        "/api/admin/option-types?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    
    # THEN: 응답이 성공적이고, 각 옵션 타입 필드가 올바르게 매핑됨
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "option_types" in data["data"]
    option_types = data["data"]["option_types"]
    assert isinstance(option_types, list)
    assert len(option_types) >= 3
    
    # 첫 번째 옵션 타입 데이터 검증
    option_type = option_types[0]
    assert "option_type_id" in option_type
    assert "option_type_name" in option_type
    assert "description" in option_type
    assert "option_type_images" in option_type
    assert "option_type_features" in option_type
    assert "option_type_size" in option_type
    assert "option_type_cost" in option_type
    assert "created_at" in option_type
    assert "created_by" in option_type
    assert "updated_at" in option_type
    assert "updated_by" in option_type

def test_get_option_type_list_unauthorized(client):
    # 인증 토큰 없이 호출 시 401 Unauthorized 반환 확인
    response = client.get("/api/admin/option-types?page=1&pageSize=10")
    assert response.status_code == 401

def test_get_option_type_list_non_admin(client, session, create_dummy_option_types, user_token):
    # GIVEN: 비관리자 토큰과 3개의 더미 옵션 타입 데이터가 준비됨
    create_dummy_option_types(3)

    # WHEN: /admin/option-types 엔드포인트를 비관리자 토큰으로 호출
    response = client.get(
        "/api/admin/option-types?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # THEN: 403 Forbidden 응답이 발생함
    assert response.status_code == 403

def test_get_option_type_list_empty(client, session, master_token):
    # GIVEN: 옵션 타입 테이블을 초기화하여 빈 상태로 만듦
    session.exec(text("DELETE FROM option_type"))
    session.commit()

    # WHEN: 관리자 토큰으로 빈 옵션 타입 목록 조회 요청
    response = client.get(
        "/api/admin/option-types?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 응답 결과는 빈 리스트이어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    option_types = data["data"]["option_types"]
    assert isinstance(option_types, list)
    assert len(option_types) == 0

def test_get_option_type_list_pagination(client, session, create_dummy_option_types, master_token, clear_option_types):
    # GIVEN: 옵션 타입 테이블 초기화 후 5개의 더미 옵션 타입 생성
    clear_option_types()  # clear_option_types fixture를 통해 DB 초기화
    create_dummy_option_types(5)

    # WHEN: 페이지 사이즈 3으로 각 페이지 요청 (page1, page2, page3)
    response1 = client.get(
        "/api/admin/option-types?page=1&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response2 = client.get(
        "/api/admin/option-types?page=2&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response3 = client.get(
        "/api/admin/option-types?page=3&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: page1은 3개, page2는 2개, page3는 빈 리스트
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert len(data1["data"]["option_types"]) == 3
    assert len(data2["data"]["option_types"]) == 2
    assert len(data3["data"]["option_types"]) == 0

def test_get_option_type_list_invalid_page(client, master_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: page 값이 0으로 GET 요청 시
    response = client.get(
        "/api/admin/option-types?page=0&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_get_option_type_list_invalid_page_size(client, master_token):
    # GIVEN: 관리자 토큰 생성
    # WHEN: pageSize 값이 0으로 GET 요청 시
    response = client.get(
        "/api/admin/option-types?page=1&pageSize=0",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 유효성 검사 실패로 422 에러가 발생함
    assert response.status_code == 422

def test_option_type_field_conversion(client, session, create_dummy_option_types, master_token, clear_option_types):
    # GIVEN: 옵션 타입 테이블 초기화 후 단일 옵션 타입 데이터 생성
    clear_option_types()
    create_dummy_option_types(1)

    # WHEN: 관리자 토큰으로 단일 옵션 타입 조회 GET 요청 수행
    response = client.get(
        "/api/admin/option-types?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: current_location이 dict로 변환되고, status가 "active"로 매핑됨
    assert response.status_code == 200
    data = response.json()
    option_types = data["data"]["option_types"]
    assert len(option_types) > 0
    option_type = option_types[0]
