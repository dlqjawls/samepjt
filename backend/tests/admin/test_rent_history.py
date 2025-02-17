import pytest
from datetime import datetime, timedelta
from sqlmodel import Session

from app.core.jwt import jwt_handler
from app.db.models.rent_history import RentHistory

from tests.helpers import master_token, create_dummy_vehicles, create_dummy_modules, create_dummy_options, create_test_rent

def create_dummy_rent_history(session, client, access_token):
    create_dummy_vehicles(session, count=3)
    create_dummy_modules(session, count=3)
    create_dummy_options(session, count=3)
    rent_id = create_test_rent(client, access_token)
    return rent_id


def test_get_rent_history_success(client, session, master_token, create_dummy_rent_history):
    """
    정상적으로 관리자 렌트 로그를 조회하는 경우:
      - DB에 dummy 데이터를 추가하고,
      - GET /admin/rent-history 엔드포인트를 호출하며,
      - 반환된 응답에 rent_history와 pagination 필드가 포함되어 있는지 확인합니다.
    """
    rent_id = create_dummy_rent_history(session, client, master_token)
    
    # When: 관리자 토큰으로 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    
    # Then: 응답 상태 코드가 200이고, 결과 코드와 데이터 구조가 올바름.
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "rent_history" in data["data"]
    assert isinstance(data["data"]["rent_history"], list)
    pagination = data["data"]["pagination"]
    assert "currentPage" in pagination
    assert "totalPages" in pagination
    assert "totalItems" in pagination
    assert "pageSize" in pagination

def test_get_rent_history_unauthorized(client):
    """
    토큰이 제공되지 않은 경우 401 에러가 발생해야 합니다.
    """
    # Given: 인증 토큰 없이 시작함.
    # When: GET 요청을 수행함.
    # Then: 상태 코드가 401임.
    response = client.get("/admin/rent-history?page=1&page_size=10")
    assert response.status_code == 401

def test_get_rent_history_non_admin(client, session):
    """
    관리자 권한이 아닌 토큰으로 조회할 때 Forbidden 응답이 반환되는지 확인합니다.
    """
    # Given: role "user"인 토큰을 생성하고, DB에 2개의 dummy 레코드를 추가함.
    access_token, _ = jwt_handler.create_token(2, role="user")
    create_dummy_rent_history(session, count=2)
    
    # When: 사용자 토큰으로 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Then: 상태 코드가 403임.
    assert response.status_code == 403

def test_get_rent_history_empty(client, session, admin_token):
    """
    DB에 아무런 렌트 기록이 없을 경우, rent_history 리스트가 빈 리스트로
    반환되고, pagination 정보 (totalItems=0, totalPages=0 등)가 올바르게 설정되는지 확인합니다.
    """
    # Given: DB에서 모든 RentHistory 데이터를 제거함.
    session.query(RentHistory).delete()
    session.commit()
    
    # When: 관리자 토큰으로 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 상태 코드가 200이고, rent_history는 빈 리스트이며, pagination은 totalItems=0, totalPages=0, currentPage=1, pageSize=10임.
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["data"]["rent_history"] == []
    pagination = data["data"]["pagination"]
    assert pagination["totalItems"] == 0
    assert pagination["totalPages"] == 0
    assert pagination["currentPage"] == 1
    assert pagination["pageSize"] == 10

@pytest.mark.parametrize("page,page_size,expected_count", [
    (1, 5, 5),  # 첫 페이지, 모든 데이터
    (1, 3, 3),  # 첫 페이지, 일부 데이터
    (2, 3, 2),  # 두번째 페이지, 나머지 데이터
    (3, 3, 0),  # 데이터 없는 페이지
])
def test_get_rent_history_pagination(client, session, admin_token, page, page_size, expected_count):
    """
    페이지네이션 동작을 다양한 페이지와 크기로 테스트합니다.
    """
    # Given: DB에 5개의 dummy 레코드를 추가함
    create_dummy_rent_history(session, count=5)
    
    # When: 페이지네이션 파라미터로 GET 요청을 수행함
    response = client.get(
        f"/admin/rent-history?page={page}&page_size={page_size}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 응답이 성공적이고 예상된 개수의 데이터가 반환됨
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert len(data["data"]["rent_history"]) == expected_count

@pytest.mark.parametrize("invalid_param,expected_error", [
    ("page=0", "ensure this value is greater than 0"),
    ("page=-1", "ensure this value is greater than 0"),
    ("page_size=0", "ensure this value is greater than 0"),
    ("page_size=-1", "ensure this value is greater than 0"),
    ("page=abc", "value is not a valid integer"),
    ("page_size=def", "value is not a valid integer"),
])
def test_get_rent_history_invalid_parameters(client, session, admin_token, invalid_param, expected_error):
    """
    잘못된 쿼리 파라미터에 대한 유효성 검사를 테스트합니다.
    """
    # Given: DB에 dummy 데이터를 추가함
    create_dummy_rent_history(session, count=3)
    
    # When: 잘못된 파라미터로 GET 요청을 수행함
    response = client.get(
        f"/admin/rent-history?{invalid_param}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 422 에러가 발생하고 적절한 에러 메시지가 포함됨
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert expected_error in str(data["detail"])

@pytest.mark.parametrize("auth_header,expected_status", [
    (None, 401),  # 헤더 없음
    ("", 401),    # 빈 헤더
    ("Bearer ", 401),  # 토큰 없는 Bearer
    ("Bearer invalid.token.here", 401),  # 잘못된 토큰
    ("Basic YWRtaW46cGFzcw==", 401),  # 잘못된 인증 방식
])
def test_get_rent_history_authentication(client, session, auth_header, expected_status):
    """
    다양한 인증 시나리오를 테스트합니다.
    """
    # Given: DB에 dummy 데이터를 추가함
    create_dummy_rent_history(session, count=3)
    
    # When: 다양한 인증 헤더로 GET 요청을 수행함
    headers = {"Authorization": auth_header} if auth_header else {}
    response = client.get("/admin/rent-history?page=1&page_size=10", headers=headers)
    
    # Then: 예상된 상태 코드가 반환됨
    assert response.status_code == expected_status
