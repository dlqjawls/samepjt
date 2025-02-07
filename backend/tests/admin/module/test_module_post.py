import pytest
from sqlmodel import Session, select, text, delete
from app.db.models.module import Module
from app.core.jwt import jwt_handler
from app.utils.lut_constants import ItemStatus
from faker import Faker

fake = Faker()

@pytest.fixture
def master_token():
    """마스터 권한 토큰 생성"""
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    """일반 관리자 권한 토큰 생성"""
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def clear_modules(session: Session):
    """모듈 테이블 초기화"""
    session.execute(delete(Module))
    session.commit()

def test_create_module_success(client, session, master_token, clear_modules):
    """✅ 정상적인 모듈 등록 테스트"""
    # Given: 모듈 등록 요청 데이터
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1
    }

    # When: 마스터 권한으로 모듈 등록 요청
    response = client.post(
        "/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module registered successfully"

    # Then: DB에 저장된 데이터 검증
    module = session.exec(select(Module).where(Module.module_nfc_tag_id == module_data["module_nfc_tag_id"])).first()
    assert module is not None
    assert module.module_nfc_tag_id == module_data["module_nfc_tag_id"]
    assert module.status_id == ItemStatus.INACTIVE


def test_create_module_duplicate_nfc_tag_id(client, session, master_token, clear_modules):
    """❌ 중복된 NFC 태그 ID로 모듈 등록 시도"""
    # Given: 기존 모듈 데이터
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1
    }
    response = client.post(
        "/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200

    # When: 동일한 NFC 태그 ID로 다시 등록 시도
    duplicate_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1
    }
    response = client.post(
        "/admin/modules",
        json=duplicate_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 409 Conflict 응답
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"]
    assert data["detail"]["module_nfc_tag_id"] == duplicate_data["module_nfc_tag_id"]

def test_create_module_invalid_format(client, master_token):
    """❌ 잘못된 형식의 데이터로 모듈 등록 시도"""
    invalid_data = [
        {
            "module_nfc_tag_id": None,
            "module_type_id": 1
        },
        {
            "module_nfc_tag_id": "1A1FF1043E2BC6",
            "module_type_id": None
        },
        {
            "module_nfc_tag_id": "1A1FF1043E2BC6",
            "module_type_id": 0
        },
        {
            "module_nfc_tag_id": "1A1FF1043E2BC6",
            "module_type_id": "ABC-1234"
        }
      ]

    for data in invalid_data:
        response = client.post(
            "/admin/modules",
            json=data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 422
        assert response.json()["resultCode"] == "FAILURE"

def test_create_module_unauthorized(client):
    """❌ 인증 없이 모듈 등록 시도"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1
    } 
    response = client.post("/admin/modules", json=module_data)
    assert response.status_code == 401

def test_create_module_forbidden(client, semi_admin_token):
    """❌ 권한 없는 사용자의 모듈 등록 시도"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1
    }
    response = client.post(
        "/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403

def test_create_module_duplicate_module_nfc_tag_id(client, session, master_token, clear_modules):
    """❌ 중복된 모듈 NFC 태그 ID로 등록 시도"""
    # Given: 기존 모듈 데이터
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1 
    }
    response = client.post(
        "/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200

    # When: 동일한 모듈 NFC 태그 ID로 다시 등록 시도
    duplicate_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": 1
    }
    response = client.post(
        "/admin/modules",
        json=duplicate_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 409 Conflict 응답
    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already exists" in data["message"]
    assert data["detail"]["module_nfc_tag_id"] == duplicate_data["module_nfc_tag_id"]

@pytest.mark.parametrize("invalid_nfc_tag_id", [
    "",  # 빈 문자열
    "A" * 51,  # 최대 길이 초과
    "TEST@123",  # 특수문자 포함
    "TEST 123",  # 공백 포함
    "TEST-123",  # 하이픈 포함
    "TEST_123",  # 언더스코어 포함
])
def test_create_module_invalid_nfc_tag_id_format(client, master_token, invalid_nfc_tag_id):
    """❌ 다양한 잘못된 모듈 NFC 태그 ID 형식으로 등록 시도"""
    module_data = {
        "module_nfc_tag_id": invalid_nfc_tag_id,
        "module_type_id": 1
    }
    response = client.post(
        "/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

@pytest.mark.parametrize("invalid_module_type_id", [
    "PBV1234",  # 하이픈 없음
    "PBV-123",  # 숫자 3자리
    "PBV-12345",  # 숫자 5자리
    "ABC-1234",  # 잘못된 접두사
    "pbv-1234",  # 소문자
    "PBV-123A",  # 문자 포함
    " PBV-1234 "  # 앞뒤 공백
])
def test_create_module_invalid_module_type_id_format(client, master_token, invalid_module_type_id):
    """❌ 다양한 잘못된 모듈 타입 ID 형식으로 등록 시도"""
    module_data = {
        "module_nfc_tag_id": "1A1FF1043E2BC6",
        "module_type_id": invalid_module_type_id
    }
    response = client.post(
        "/admin/modules",
        json=module_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"

def test_create_module_missing_fields(client, master_token):
    """❌ 필수 필드 누락 테스트"""
    invalid_data_list = [
        {},  # 모든 필드 누락
        {"module_nfc_tag_id": "1A1FF1043E2BC6"},  # module_nfc_tag_id 누락
        {"module_nfc_tag_id": "PBV-1234"},  # module_type_id 누락
        {"module_nfc_tag_id": None, "module_type_id": "PBV-1234"},  # module_nfc_tag_id이 null
        {"module_nfc_tag_id": "1A1FF1043E2BC6", "module_type_id": None}  # module_type_id가 null
    ]

    for data in invalid_data_list:
        response = client.post(
            "/admin/modules",
            json=data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 422
        assert response.json()["resultCode"] == "FAILURE"

def test_create_multiple_modules_success(client, session, master_token, clear_modules):
    """✅ 여러 모듈 연속 등록 테스트"""
    modules_data = [
        {"module_nfc_tag_id": f"{fake.hexify(text='^^^^^^^^^^^^^^', upper=True)}", "module_type_id": 1}
        for i in range(1, 4)
    ]

    for module_data in modules_data:
        response = client.post(
            "/admin/modules",
            json=module_data,
            headers={"Authorization": f"Bearer {master_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["resultCode"] == "SUCCESS"

    # DB에 모든 모듈이 저장되었는지 확인
    for module_data in modules_data:
        module = session.exec(
            select(Module).where(Module.module_nfc_tag_id == module_data["module_nfc_tag_id"])
        ).first()
        assert module is not None
        assert module.module_nfc_tag_id == module_data["module_nfc_tag_id"]
