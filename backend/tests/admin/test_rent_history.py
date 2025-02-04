import pytest
from datetime import datetime, timedelta
from sqlmodel import Session

from app.core.jwt import jwt_handler
from app.models.rent_history import RentHistory

@pytest.fixture
def admin_token():
    # JWTHandler의 create_token()은 (access_token, refresh_token)을 반환합니다.
    access_token, _ = jwt_handler.create_token(1, role="master")
    return access_token

def create_dummy_rent_history(session: Session, count: int = 5):
    """
    DB에 dummy 렌트 기록을 추가하는 헬퍼 함수.
    각 레코드에는 기본 필드 값이 포함됩니다.
    """
    dummy_records = []
    now = datetime.now()
    for i in range(count):
        rent = RentHistory(
            user_pk=i + 1,
            departure_location="12.345,67.890",
            arrival_location="98.765,43.210",
            cost=100.0 * (i + 1),
            mileage=10.0 * (i + 1),
            status_id=1,  # in_progress
            created_at=now - timedelta(days=i),
            updated_at=now - timedelta(days=i)
        )
        session.add(rent)
        dummy_records.append(rent)
    session.commit()
    return dummy_records

def test_get_rent_history_success(client, session, admin_token):
    """
    정상적으로 관리자 렌트 로그를 조회하는 경우:
      - DB에 dummy 데이터를 추가하고,
      - GET /admin/rent-history 엔드포인트를 호출하며,
      - 반환된 응답에 rent_history와 pagination 필드가 포함되어 있는지 확인합니다.
    """
    # Given: DB에 3개의 dummy 레코드를 추가함.
    create_dummy_rent_history(session, count=3)
    
    # When: 관리자 토큰으로 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"}
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

def test_get_rent_history_pagination(client, session, admin_token):
    """
    dummy 데이터를 7건 추가한 후, page_size=3로 페이지네이션한 결과를 검증합니다.
    """
    # Given: DB에 7개의 dummy 레코드를 추가함.
    create_dummy_rent_history(session, count=7)
    
    # When: 관리자 토큰으로 페이지 번호 2, page_size=3의 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=2&page_size=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 상태 코드가 200이고, pagination은 totalItems=7, pageSize=3, currentPage=2, totalPages=3이며, rent_history 리스트의 길이는 3임.
    assert response.status_code == 200
    data = response.json()
    pagination = data["data"]["pagination"]
    assert pagination["totalItems"] == 7
    assert pagination["pageSize"] == 3
    assert pagination["currentPage"] == 2
    assert pagination["totalPages"] == 3
    assert len(data["data"]["rent_history"]) == 3

def test_get_rent_history_invalid_query_parameters(client, admin_token):
    """
    page, page_size 파라미터에 잘못된 값 (0, 음수, 문자열 등)이 입력된 경우 422 에러가 반환되는지 확인합니다.
    """
    # Given: 잘못된 page 및 page_size 값을 사용함.
    # When: page=0인 경우 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=0&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Then: 상태 코드가 422임.
    assert response.status_code == 422
    
    # When: page_size=0인 경우 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Then: 상태 코드가 422임.
    assert response.status_code == 422
    
    # When: 비정수형 문자열을 사용한 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=abc&page_size=def",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Then: 상태 코드가 422임.
    assert response.status_code == 422

def test_get_rent_history_page_out_of_range(client, session, admin_token):
    """
    존재하지 않는 페이지 번호로 호출 시, rent_history 리스트가 빈 리스트로 반환되는지 확인합니다.
    """
    # Given: DB에 3개의 dummy 레코드를 추가함.
    create_dummy_rent_history(session, count=3)
    
    # When: 존재하지 않는 페이지 번호(예: page=10, page_size=3)로 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=10&page_size=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 상태 코드가 200이고, 반환된 rent_history 리스트는 빈 리스트이며, pagination은 totalItems=3, totalPages=1, currentPage=10임.
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["rent_history"] == []
    pagination = data["data"]["pagination"]
    assert pagination["totalItems"] == 3
    assert pagination["totalPages"] == 1
    assert pagination["currentPage"] == 10

def test_get_rent_history_missing_query_parameters(client, session, admin_token):
    """
    사용자가 page 및 page_size 파라미터 없이 요청한 경우, 기본값이 적용되어 올바른 결과가 반환되는지 확인합니다.    
    """
    # Given: DB에 5개의 dummy 레코드를 추가함.
    create_dummy_rent_history(session, count=5)
    
    # When: page 및 page_size 파라미터 없이 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 상태 코드가 200이고, 결과 코드와 데이터 구조가 올바름.
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    pagination = data["data"]["pagination"]
    assert pagination["currentPage"] == 1
    assert pagination["pageSize"] == 10
    assert len(data["data"]["rent_history"]) == 5

def test_get_rent_history_invalid_authorization_format(client, session, admin_token):
    """
    잘못된 형식의 인증 헤더를 사용한 경우, 401 에러가 발생하는지 확인합니다.
    """
    # Given: DB에 3개의 dummy 레코드를 추가함.
    create_dummy_rent_history(session, count=3)
    
    # When: 잘못된 형식의 인증 헤더를 사용한 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": f"{admin_token}"}
    )
    
    # Then: 상태 코드가 401임.
    assert response.status_code == 401

def test_get_rent_history_invalid_token(client, session):
    """
    유효하지 않은 토큰이 제공된 경우, 401 에러가 발생하는지 확인합니다.
    """
    # Given: 유효하지 않은 토큰을 사용함.
    # When: GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": "Bearer invalid.token.value"}
    )
    
    # Then: 상태 코드가 401임.
    assert response.status_code == 401

def test_get_rent_history_ordering(client, session, admin_token):
    """
    DB에 추가된 dummy 데이터를 시간 기준 최신순으로 반환되는지 확인합니다.    
    """
    # Given: DB에 5개의 dummy 레코드를 추가함 (user_pk가 낮을수록 최신).
    create_dummy_rent_history(session, count=5)
    
    # When: 관리자 토큰으로 GET 요청을 수행함.
    response = client.get(
        "/admin/rent-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: 응답 상태 코드가 200이고, 반환된 rent_history 리스트의 첫 번째 항목의 user_pk가 1임.
    assert response.status_code == 200
    data = response.json()
    rent_history_list = data["data"]["rent_history"]
    assert rent_history_list[0]["user_pk"] == 1
