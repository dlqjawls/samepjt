import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.jwt import jwt_handler

from tests.helpers import master_token, user_token

def test_get_maintenance_status_success(client: TestClient, master_token):
    headers = {"Authorization": f"Bearer {master_token}"}
    response = client.get("/api/admin/maintenance-status", headers=headers)
    assert response.status_code == 200
    assert response.json()["resultCode"] == "SUCCESS"
    assert response.json()["data"]["maintenance_statuses"]

def test_get_maintenance_status_unauthorized(client: TestClient, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/admin/maintenance-status", headers=headers)
    assert response.status_code == 403
    assert response.json()["resultCode"] == "FAILURE"
    assert response.json()["message"] == "Permission denied"

def test_get_maintenance_status_empty(client: TestClient, master_token, session):
    # 정비 상태 테이블 초기화
    session.exec(text("DELETE FROM lut_maintenance_status"))
    session.commit()

    headers = {"Authorization": f"Bearer {master_token}"}
    response = client.get("/api/admin/maintenance-status", headers=headers)
    assert response.status_code == 200
    assert response.json()["resultCode"] == "SUCCESS"
    assert response.json()["data"]["maintenance_statuses"] == []