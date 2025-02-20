from datetime import datetime
import pytest
from sqlmodel import Session
from app.db.models.maintenance_history import MaintenanceHistory
from sqlalchemy import text

from tests.helpers import master_token, user_token

# GIVEN: 정비 기록 테이블 초기화 헬퍼
@pytest.fixture
def clear_maintenance_histories(session: Session):
    def _clear():
        session.exec(text("DELETE FROM maintenance_history"))
        session.commit()
    return _clear

# GIVEN: 더미 정비 기록 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_maintenance_histories(session: Session):
    def _create(*, count: int = 1, start_item_id: int = 1, item_type_id: int = 1):
        maintenance_histories = []
        for i in range(count):
            maintenance_history = MaintenanceHistory(
                item_id=start_item_id + i,
                item_type_id=item_type_id,
                issue=f"ISSUE {start_item_id + i} for item_type {item_type_id}",
                cost=10000,
                maintenance_status_id=1,
                scheduled_at=datetime.now(),
                completed_at=datetime.now(),
                created_by=1,
                updated_by=1
            )
            session.add(maintenance_history)
            maintenance_histories.append(maintenance_history)
        session.commit()
        return maintenance_histories
    return _create

def test_get_maintenance_history_list_success(client, session, create_dummy_maintenance_histories, master_token):
    # GIVEN: 관리자 토큰과 3개의 더미 정비 기록 데이터가 준비됨
    create_dummy_maintenance_histories(count=3, start_item_id=1, item_type_id=1)

    # WHEN: /admin/maintenance-history 엔드포인트를 GET 요청
    response = client.get(
        "/api/admin/maintenance-history?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "maintenance_history" in data["data"]
    maintenance_histories = data["data"]["maintenance_history"]
    assert isinstance(maintenance_histories, list)
    assert len(maintenance_histories) >= 3

def test_get_maintenance_history_list_unauthorized(client):
    # 인증 토큰 없이 호출 시 401 Unauthorized 반환 확인
    response = client.get("/api/admin/maintenance-history?page=1&pageSize=10")
    assert response.status_code == 401

def test_get_maintenance_history_list_non_admin(client, session, create_dummy_maintenance_histories, user_token):
      # GIVEN: 비관리자 토큰과 3개의 더미 정비 기록 데이터가 준비됨
    create_dummy_maintenance_histories(count=3, start_item_id=1, item_type_id=1)

    # WHEN: /admin/maintenance-history 엔드포인트를 비관리자 토큰으로 호출
    response = client.get(
        "/api/admin/maintenance-history?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # THEN: 403 Forbidden 응답이 발생함
    assert response.status_code == 403

def test_get_maintenance_history_list_empty(client, session, master_token):
    # GIVEN: 정비 기록 테이블을 초기화하여 빈 상태로 만듦
    session.exec(text("DELETE FROM maintenance_history"))
    session.commit()

    # WHEN: 관리자 토큰으로 빈 정비 기록 목록 조회 요청
    response = client.get(
        "/api/admin/maintenance-history?page=1&pageSize=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # THEN: 응답 결과는 빈 리스트이어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    maintenance_histories = data["data"]["maintenance_history"]
    assert isinstance(maintenance_histories, list)
    assert len(maintenance_histories) == 0

def test_get_maintenance_history_list_pagination(client, session, create_dummy_maintenance_histories, master_token, clear_maintenance_histories):
    # GIVEN: 정비 기록 테이블 초기화 후 5개의 더미 정비 기록 생성
    clear_maintenance_histories()  # clear_maintenance_histories fixture를 통해 DB 초기화
    create_dummy_maintenance_histories(count=5, start_item_id=1, item_type_id=1)

    # WHEN: 페이지 사이즈 3으로 각 페이지 요청 (page1, page2, page3)
    response1 = client.get(
        "/api/admin/maintenance-history?page=1&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response2 = client.get(
        "/api/admin/maintenance-history?page=2&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    response3 = client.get(
        "/api/admin/maintenance-history?page=3&pageSize=3",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # THEN: page1은 3개, page2는 2개, page3는 빈 리스트
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert len(data1["data"]["maintenance_history"]) == 3
    assert len(data2["data"]["maintenance_history"]) == 2
    assert len(data3["data"]["maintenance_history"]) == 0

@pytest.mark.parametrize("page, pageSize", [
    (0, 10),
    (1, 0)
])
def test_get_maintenance_history_list_invalid_queries(client, master_token, page, pageSize):
    response = client.get(
        f"/api/admin/maintenance-history?page={page}&pageSize={pageSize}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422

def test_get_maintenance_history_query_filters(client, session, create_dummy_maintenance_histories, master_token, clear_maintenance_histories):
    # GIVEN: DB 초기화 후, 여러 아이템 타입의 정비 기록 생성
    clear_maintenance_histories()
    # 차량 (assumed vehicle) 정비 기록 2개 : item_type_id=1
    create_dummy_maintenance_histories(count=2, start_item_id=1, item_type_id=1)
    # 모듈 정비 기록 3개: item_type_id=2
    create_dummy_maintenance_histories(count=3, start_item_id=10, item_type_id=2)
    # 옵션 정비 기록 4개: item_type_id=3
    create_dummy_maintenance_histories(count=4, start_item_id=20, item_type_id=3)

    # WHEN: 특정 아이템 타입 "vehicle" (item_type_id=1)으로 필터링
    response = client.get(
        "/api/admin/maintenance-history?page=1&pageSize=10&item_type=vehicle",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    records = data["data"]["maintenance_history"]
    for rec in records:
        # 스키마의 item_type 필드로 문자열(예: "vehicle") 반환
        assert rec["item_type_name"].lower() == "vehicle"

    # WHEN: 특정 item_type "module"과 특정 item_id (예: 11)로 필터링
    response = client.get(
        "/api/admin/maintenance-history?page=1&pageSize=10&item_type=module&item_id=11",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    records = data["data"]["maintenance_history"]
    # 해당 조건에 맞는 정비 기록이 1건만 조회되어야 함
    assert len(records) == 1
    assert records[0]["item_id"] == 11

@pytest.mark.parametrize("start_item_id, item_type_id, count", [
    (1, 1, 3),
    (10, 2, 2),
    (20, 3, 4)
])
def test_create_dummy_maintenance_histories(session: Session, create_dummy_maintenance_histories, start_item_id, item_type_id, count):
    records = create_dummy_maintenance_histories(count=count, start_item_id=start_item_id, item_type_id=item_type_id)
    assert len(records) == count
    assert records[0].item_id == start_item_id
    assert records[0].item_type_id == item_type_id
