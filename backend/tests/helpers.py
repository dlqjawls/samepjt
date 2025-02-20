import json
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.jwt import jwt_handler
import pytest

from app.db.models.module import Module
from app.db.models.option import Option
from app.db.models.vehicle import Vehicle
from app.utils.lut_constants import ItemStatus, ModuleType

test_base64_img = "data:image/gif;base64,R0lGODlhAAEAAcQAALe9v9ve3/b393mDiJScoO3u74KMkMnNz4uUmKatsOTm552kqK+1uNLW18DFx3B7gP///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C1hNUCBEYXRhWE1QPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS4wLWMwNjAgNjEuMTM0Nzc3LCAyMDEwLzAyLzEyLTE3OjMyOjAwICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjAxODAxMTc0MDcyMDY4MTE5QjEwQjYyNTc4MkUxRURBIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjEzN0VEMDZBQjMyNzExRTE4REMzRUZGMkFCOTM1NkZBIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjEzN0VEMDY5QjMyNzExRTE4REMzRUZGMkFCOTM1NkZBIiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCBDUzUgTWFjaW50b3NoIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MDI4MDExNzQwNzIwNjgxMTlCMTBCNjI1NzgyRTFFREEiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6MDE4MDExNzQwNzIwNjgxMTlCMTBCNjI1NzgyRTFFREEiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4B//79/Pv6+fj39vX08/Lx8O/u7ezr6uno5+bl5OPi4eDf3t3c29rZ2NfW1dTT0tHQz87NzMvKycjHxsXEw8LBwL++vby7urm4t7a1tLOysbCvrq2sq6qpqKempaSjoqGgn56dnJuamZiXlpWUk5KRkI+OjYyLiomIh4aFhIOCgYB/fn18e3p5eHd2dXRzcnFwb25tbGtqaWhnZmVkY2JhYF9eXVxbWllYV1ZVVFNSUVBPTk1MS0pJSEdGRURDQkFAPz49PDs6OTg3NjU0MzIxMC8uLSwrKikoJyYlJCMiISAfHh0cGxoZGBcWFRQTEhEQDw4NDAsKCQgHBgUEAwIBAAAh+QQAAAAAACwAAAAAAAEAAQAF/yAkjmRpnmiqrmzrvnAsz3Rt33iu73zv/8CgcEgsGo/IpHLJbDqf0Kh0Sq1ar9isdsvter/gsHhMLpvP6LR6zW673/C4fE6v2+/4vH7P7/v/gIGCg4SFhoeIiYptBQEADAQED5OUlQ8DkQwAAQKLni0KDgsDlqWmpQYLDgqfrSINCQans7SWBgkNrogFDKS1v8APBgwFuoIBksHKwQsBxn3Iy9LKBM7PdwXJ09vAC8XXcwDc48EDAOBwCgjk7MAI3+hqB77t9bMDufFoDPb9tef6yiTwR3BWgoBiBKwryLDUQYRftDWcOOkhxC0DKWqseFGLuI0gHXS80gCkyQfWRv9KKUDvJMUBnVRGkeiS4gKZUA7UPJkP5xIBLXdSNOCTyUehIAEWPQIUqUmYS48cdbrxQFQjsqiCJHp1SEmtJlN2/ZER7EaLY30ENdtwQNofAdiaZPWWx1S5E0XW3UETL8Obe3Ws9UuQa+AbAghvPIwjrmKKYhnLcPy4YWTJMBxUntgTc4y7m/sp9QwDdOh6o0m7MH2aXWrVLFi3HmcV9ouvs+1dtp2Ccu52u3mfKPDbXkzhLIrXQ+5ioXJuBJi34PecGwPpLHRW39YZ+4nE26cd947CeXhg0cmr0Hw+WG31JQQ4AFC2fS1NB8aTVzDY/q8BdJHXlH/bQEUeewRuo5f/d30lGEx63jnIjVvkSciNehZug2GG0mzIoTIefgiMelmJWAuE2DVooiUoSkfdirO8hpx2MJ7yHnYK1DgLPN71B6Nh5NWn4yTXwefbkA8ESCKSkyAA3wg0DnkjfCXW6OSTIxy5YnBB6lgkliMoBCMC+oHJkolkgjmceRKmqeZ3APi4nTlvriDAAQCo+BsBADRQZp0o4LYdl4CiIOdpQBY6XXhfKgpKeDw6ygKbubUo6QpR/jblpSscqliinK4gW2UyhooCcb8ZaGoLQoaG1qoroDpbpLCq0Opjr9aqgqyh0aprCrf6Veqv33lKlarExrbZgsm2UCVeVzbrgpZsESqt/wkLEJbrtSqMihSz3K5ArVbWhjsCr2z9ae4JhK3bHF6WunuCnkIBJq8KL5o17L0ieFvTvvz661J3/JYwLlLlynuwUAm7u/BODa/7cE0RmzuxSxWHe/FJGXO7cVgFp5ApuSGjIPBJAN8bLFKNljzCs1pF67II6JqlbsCEgRvygHghW7CYirlZsDqbvVNwA8ZqhY+8BWSb2wI36xqncnRKewDMvxmwqalX+1cNrF07+PWlYWeodaHyYW2hAQ5EjRwvSSc4ADHqBeA0k5Qk0PFYd6qNt9Zuv6VAAnEPOUACSu51J6V4/0LA1lENXnjjlhyeOE6LU24PAvnhFMDKmo9z+P/euzjgd+j1sO2rKw3cjfpGCxC8CNyv72QAAKsTUgDotYOUQO6AnNz7RinrUQDjwyMlNCD8Jd/z5XsEMLnzGwH4x8fUu2Q9H81nT9j2eZzpvWI+0wH0+EHnwTv6WrUsh6DsK0Z6GDzH/2ng+9gfWvFm1Ky/XwMAHhrW9z+t8G8M4ClgZconDwWGBnJocJ0DCWOvNkxwMxRixAU3g78wYG+DFHOD8EBYE53lj4SEOWBEUEiYeJ3hdCwUiszUEMN2sSFHNcSLAMMAvxySbA0j9KFGVMgFAgoRJO4zA72OeBIXkmF6TCwIqMqQwChSZQ0ftCJD5leFkWmxJrIbQxC/SBD/ImZBgmR0ybbGsMQ0TsSJYXAjUjLYPzkipYNayKId68FFKSBojyeB4BfGCEjXoKGNhfRHBcmAvEQyBI5ecKRLzoBDSYJkh3m0JMjKQEhNTsOEX8iXJxtiRiogcpTkgOQWYIhKdswwjq2kSBn0GEtlQK8LPaxlP/rYhE7q8heljMIff9kPUHLBf8RkByaxgMZkjmOR9GOlM39hADxigWjT5AYCbkm/ZmazFlBjA9K+CYyluUEAUyOnKcxhzYSYTp2UYFs7zdA6csaOD3fypicX0DlACAAW0iTjLfxUugUENIepcMAyBVGAA0DCigRgwAEWqggF4IkAB82eAfh0AG5eaCQAeFrAKSlHgAUA4AC8DIgAAtCAR0QCb5noEyfgo4AAOMKlBGhkaxAQ000EwKOSqqlN8QSAooo0EpHQKTl4itSSFrWoKLUpUGdG1apa9apYzapWt8rVrnr1q2ANq1jHStaymvWseggBADs="


# GIVEN: 관리자 토큰 생성 (role "master")
@pytest.fixture
def master_token():
    return jwt_handler.create_token(1, role="master")[0]

# GIVEN: 일반 관리자 토큰 생성 (role "semi")
@pytest.fixture
def semi_admin_token():
    return jwt_handler.create_token(2, role="semi")[0]  

# GIVEN: 비관리자 토큰 생성 (role "user")
@pytest.fixture
def user_token():
    return jwt_handler.create_token(2, role="user")[0]
  
# GIVEN: 더미 차량 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_vehicles(session: Session):
    def _create(count: int = 3):
        vehicles = []
        for i in range(count):
            # JSON 형식의 좌표 문자열 생성
            location = json.dumps({"x": 12.313, "y": 32.3232})
            vehicle = Vehicle(
                vin=f"VIN{i+1}",
                vehicle_number=f"PBV-123{i+1}",
                current_location=location,  # JSON 문자열로 저장
                mileage=1000.0 * (i+1),
                last_maintenance_at=datetime.now(),
                next_maintenance_at=datetime.now(),
                item_status_id=ItemStatus.INACTIVE.ID,
                created_by=1,
                updated_by=1
            )
            session.add(vehicle)
            vehicles.append(vehicle)
        session.commit()
        return vehicles
    return _create

# GIVEN: 더미 옵션 데이터를 생성하는 헬퍼 함수
@pytest.fixture
def create_dummy_options(session: Session):
    def _create(count: int = 3):
        options = []
        for i in range(count):
            # JSON 형식의 좌표 문자열 생성
            option = Option(
                option_type_id=1,
                item_status_id=ItemStatus.INACTIVE.ID, 
                created_by=1,
                updated_by=1
            )
            session.add(option)
            options.append(option)
        session.commit()
        return options
    return _create
  
 
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
                module_type_id=ModuleType.MEDIUM.ID,
                current_location=location,  # JSON 문자열로 저장
                item_status_id=ItemStatus.INACTIVE.ID,
                created_by=1,
                updated_by=1
            )
            session.add(module)
            modules.append(module)
        session.commit()
        return modules
    return _create
   
def register_and_login(
    client: TestClient,
    user_id: str = "testuser",
    password: str = "test1234"
) -> str:
    """테스트용 사용자 등록 및 로그인 후 access_token 반환
    
    Args:
        client: TestClient 인스턴스
        user_id: 사용자 ID (기본값: "testuser")
        password: 비밀번호 (기본값: "test1234")
        
    Returns:
        str: JWT access token
    """
    # 회원가입 요청
    register_payload = {
        "id": user_id,
        "password": password,
        "email": f"{user_id}@example.com",
        "name": f"{user_id}님",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    # 로그인 요청
    login_payload = {
        "id": user_id,
        "password": password
    }
    login_response = client.post("/auth/login", json=login_payload)
    return login_response.json()["data"]["access_token"]

def create_valid_rent_request(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """유효한 렌트 요청 데이터 생성
    
    Args:
        start_date: 렌트 시작일 (기본값: 현재 + 1일)
        end_date: 렌트 종료일 (기본값: 현재 + 2일)
        
    Returns:
        Dict: 렌트 요청 데이터
    """
    if not start_date:
        start_date = datetime.now() + timedelta(days=1)
    if not end_date:
        end_date = datetime.now() + timedelta(days=2)

    return {
        "selectedOptionTypes": [
            {"optionTypeId": 1, "quantity": 1},
            {"optionTypeId": 2, "quantity": 1}
        ],
        "autonomousArrivalPoint": {"x": 12.313, "y": 32.3232},
        "autonomousDeparturePoint": {"x": 11.512, "y": 30.4531},
        "rentStartDate": start_date.isoformat(),
        "rentEndDate": end_date.isoformat()
    }

def create_test_rent(client: TestClient, access_token: str) -> int:
    """렌트 요청을 생성하고 rent_id 반환
    
    Args:
        client: TestClient 인스턴스
        access_token: JWT access token
        
    Returns:
        int: 생성된 렌트 ID
    """
    rent_request = create_valid_rent_request()
    response = client.post(
        "/api/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()["data"]["rent_id"]