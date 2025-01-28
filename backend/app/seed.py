# app/seeder.py

from datetime import datetime, timedelta
import random
import json
import os
from faker import Faker
from sqlmodel import Session

# 모델들 전부 import (또는 from app.models import * 로 import)
from app.models import (
    Role, ItemStatus, ItemType, ModuleType,
    MaintenanceStatus, UsageStatus, RentStatus, VideoType,
    PaymentStatus, PaymentMethod,
    User, Vehicle, Module, OptionType, Option,
    ModuleSet, ModuleSetOptionTypes
)
from app.utils.bcrypt import hash_password

fake = Faker()

def seed_data(session: Session) -> None:
    """
    초기 데이터를 삽입하는 함수. 
    'session' 인자를 통해 외부(테스트 or 운영)에서 넘긴 DB 세션을 사용.
    """
    try:
        # 📌 역할(Role) 데이터 삽입
        roles = [
            Role(role_id=1, role_name="master"),
            Role(role_id=2, role_name="semi"),
            Role(role_id=3, role_name="user")
        ]
        session.add_all(roles)

        # 📌 아이템 상태(Item Status)
        item_statuses = [
            ItemStatus(item_status_id=1, item_status_name="active"),
            ItemStatus(item_status_id=2, item_status_name="inactive"),
            ItemStatus(item_status_id=3, item_status_name="maintenance")
        ]
        session.add_all(item_statuses)

        # 📌 아이템 유형(Item Type)
        item_types = [
            ItemType(item_type_id=1, item_type_name="vehicle"),
            ItemType(item_type_id=2, item_type_name="module"),
            ItemType(item_type_id=3, item_type_name="option")
        ]
        session.add_all(item_types)

        # 📌 모듈 유형(Module Type)
        module_types = [
            ModuleType(module_type_id=1, module_type_name="small", module_type_size="S", module_type_cost=100.0),
            ModuleType(module_type_id=2, module_type_name="medium", module_type_size="M", module_type_cost=200.0),
            ModuleType(module_type_id=3, module_type_name="large", module_type_size="L", module_type_cost=300.0)
        ]
        session.add_all(module_types)

        # 📌 유지보수 상태(Maintenance Status)
        maintenance_statuses = [
            MaintenanceStatus(maintenance_status_id=1, maintenance_status_name="pending"),
            MaintenanceStatus(maintenance_status_id=2, maintenance_status_name="in_progress"),
            MaintenanceStatus(maintenance_status_id=3, maintenance_status_name="completed")
        ]
        session.add_all(maintenance_statuses)

        # 📌 사용 기록 상태(Usage Status)
        usage_statuses = [
            UsageStatus(usage_status_id=1, usage_status_name="in_use"),
            UsageStatus(usage_status_id=2, usage_status_name="completed")
        ]
        session.add_all(usage_statuses)

        # 📌 대여 상태(Rent Status)
        rent_statuses = [
            RentStatus(rent_status_id=1, rent_status_name="in_progress"),
            RentStatus(rent_status_id=2, rent_status_name="completed"),
            RentStatus(rent_status_id=3, rent_status_name="canceled")
        ]
        session.add_all(rent_statuses)

        # 📌 비디오 유형(Video Type)
        video_types = [
            VideoType(video_type_id=1, video_type_name="module"),
            VideoType(video_type_id=2, video_type_name="autonomous driving")
        ]
        session.add_all(video_types)

        # 📌 결제 상태(Payment Status)
        payment_statuses = [
            PaymentStatus(payment_status_id=1, payment_status_name="pending", payment_type_id=1),
            PaymentStatus(payment_status_id=2, payment_status_name="completed", payment_type_id=1),
            PaymentStatus(payment_status_id=3, payment_status_name="failed", payment_type_id=1),
            PaymentStatus(payment_status_id=4, payment_status_name="refunded", payment_type_id=2)
        ]
        session.add_all(payment_statuses)

        # 📌 결제 방식(Payment Method)
        payment_methods = [
            PaymentMethod(payment_method_id=1, payment_method_name="credit_card"),
            PaymentMethod(payment_method_id=2, payment_method_name="bank_transfer"),
            PaymentMethod(payment_method_id=3, payment_method_name="paypal")
        ]
        session.add_all(payment_methods)

        # 📌 사용자 데이터 삽입
        base_date = datetime.now()
        dummy_users = [
            {
                "user_pk": 1,
                "user_id": "admin",
                "user_password": hash_password("admin123"),
                "user_email": "admin@example.com",
                "user_name": "Administrator",
                "user_phone_num": "010-0000-0000",
                "user_address": "Seoul, Korea",
                "role_id": 1,
                "created_at": base_date,
                "created_by": 1,
                "updated_at": base_date,
                "updated_by": 1,
                "deleted_at": None
            },
            {
                "user_pk": 2,
                "user_id": "semiadmin",
                "user_password": hash_password("semi123"),
                "user_email": "semiadmin@example.com",
                "user_name": "Semi Administrator",
                "user_phone_num": "010-1111-1111",
                "user_address": "Busan, Korea",
                "role_id": 2,
                "created_at": base_date,
                "created_by": 1,
                "updated_at": base_date,
                "updated_by": 1,
                "deleted_at": None
            },
            {
                "user_pk": 3,
                "user_id": "user",
                "user_password": hash_password("user123"),
                "user_email": "user@example.com",
                "user_name": "Regular User",
                "user_phone_num": "010-2222-2222",
                "user_address": "Incheon, Korea",
                "role_id": 3,
                "created_at": base_date,
                "created_by": 1,
                "updated_at": base_date,
                "updated_by": 1,
                "deleted_at": None
            }
        ]
        session.add_all([User(**user) for user in dummy_users])

        # 📌 차량 데이터 삽입
        dummy_vehicles = [
            {
                "vehicle_id": i,
                "vin": fake.uuid4(),
                "vehicle_number": f"PBV-{i}",
                "current_location": json.dumps({"x": i, "y": i}),
                "mileage": random.randint(1000, 5000),
                "last_maintenance_at": base_date.isoformat(),
                "next_maintenance_at": (base_date + timedelta(days=90)).isoformat(),
                "status_id": 2,
                "created_at": base_date,
                "created_by": 1,
                "updated_at": base_date,
                "updated_by": 1,
                "deleted_at": None
            }
            for i in range(3)
        ]
        session.add_all([Vehicle(**vehicle) for vehicle in dummy_vehicles])

        # 📌 모듈 데이터 삽입
        dummy_modules = [
            {
                "module_id": i,
                "module_nfc_tag_id": fake.uuid4(),
                "module_type": 1,
                "status_id": 2,
                "last_maintenance_at": base_date.isoformat(),
                "next_maintenance_at": base_date.isoformat(),
                "current_location": json.dumps({"x": 0, "y": 0}),
                "created_at": base_date,
                "created_by": 1,
                "updated_at": base_date,
                "updated_by": 1,
                "deleted_at": None
            }
            for i in range(3)
        ]
        session.add_all([Module(**module) for module in dummy_modules])

        # 📌 옵션 유형 데이터 삽입
        option_type_data = [
            {"optionTypeName": "침대", "displayFeatures": [], "description": "푹신한 침대입니다."},
            {"optionTypeName": "테이블", "displayFeatures": [], "description": "넓은 테이블입니다."},
            {"optionTypeName": "의자", "displayFeatures": [], "description": "편안한 의자입니다."},
            {"optionTypeName": "냉장고", "displayFeatures": [], "description": "음식을 보관할 수 있습니다."},
            {"optionTypeName": "배터리", "displayFeatures": ["배터리 잔여량"], "description": "전력을 공급합니다."},
            {"optionTypeName": "수납장", "displayFeatures": [], "description": "물건을 보관할 수 있습니다."},
            {"optionTypeName": "물탱크", "displayFeatures": ["물탱크 잔여량", "폐수량"], "description": "물을 저장합니다."},
            {"optionTypeName": "냉난방기", "displayFeatures": ["실내온도"], "description": "실내 온도를 조절합니다."},
            {"optionTypeName": "조명", "displayFeatures": ["조명세기"], "description": "실내 조명을 제공합니다."},
            {"optionTypeName": "대형모니터", "displayFeatures": [], "description": "대형 화면을 제공합니다."},
            {"optionTypeName": "좌변기", "displayFeatures": [], "description": "좌변기 옵션입니다."},
            {"optionTypeName": "세면대", "displayFeatures": [], "description": "세면대 옵션입니다."},
            {"optionTypeName": "거울", "displayFeatures": [], "description": "거울 옵션입니다."},
            {"optionTypeName": "간이계단", "displayFeatures": [], "description": "간이계단 옵션입니다."},
            {"optionTypeName": "LPG", "displayFeatures": [], "description": "LPG 옵션입니다."},
            {"optionTypeName": "버너", "displayFeatures": [], "description": "버너 옵션입니다."},
            {"optionTypeName": "싱크대", "displayFeatures": [], "description": "싱크대 옵션입니다."},
            {"optionTypeName": "튀김기", "displayFeatures": [], "description": "튀김기 옵션입니다."},
            {"optionTypeName": "냄비", "displayFeatures": [], "description": "냄비 옵션입니다."},
            {"optionTypeName": "전자레인지", "displayFeatures": [], "description": "전자레인지 옵션입니다."},
            {"optionTypeName": "에어컨", "displayFeatures": ["실내온도"], "description": "에어컨 옵션입니다."},
            {"optionTypeName": "커피 머신", "displayFeatures": ["커피머신 잔량"], "description": "커피 머신 옵션입니다."},
            {"optionTypeName": "자판기", "displayFeatures": ["자판기 물품 재고량"], "description": "자판기 옵션입니다."}
        ]

        dummy_option_types = [
            {
                "option_type_id": i,
                "option_type_name": option["optionTypeName"],
                "option_type_size": f"{random.randint(1, 3)}x{random.randint(1, 3)}",
                "option_type_cost": round(random.uniform(10.0, 100.0), 2),
                "description": option["description"],
                "option_type_images": fake.image_url(),
                "option_type_features": ", ".join(option["displayFeatures"]),
                "created_at": base_date,
                "updated_at": base_date,
                "created_by": 1,
                "updated_by": 1,
            }
            for i, option in enumerate(option_type_data)
        ]
        session.add_all([OptionType(**option_type) for option_type in dummy_option_types])

        # 📌 옵션 데이터 삽입
        dummy_options = []
        option_count = 3  # 각 옵션 타입당 생성할 옵션 개수
        for option_type in dummy_option_types:
            for _ in range(option_count):
                option = {
                    "option_id": len(dummy_options),
                    "option_type_id": option_type["option_type_id"],
                    "status_id": 2,
                    "created_at": base_date,
                    "updated_at": base_date,
                    "created_by": 1,
                    "updated_by": 1,
                }
                dummy_options.append(option)
        session.add_all([Option(**option) for option in dummy_options])

        # 📌 모듈 세트 데이터 삽입
        module_set_data = [
            {"moduleSetName": "기본본 모듈", "defaultOptionTypes": ["조명"]},
            {"moduleSetName": "캠핑 모듈", "defaultOptionTypes": ["침대", "테이블", "의자", "냉장고", "배터리", "수납장", "물탱크", "냉난방기", "조명"]},
            {"moduleSetName": "오피스 모듈", "defaultOptionTypes": ["테이블", "의자", "대형모니터", "배터리", "냉장고"]},
            {"moduleSetName": "화장실 모듈", "defaultOptionTypes": ["좌변기", "세면대", "거울", "간이계단"]},
            {"moduleSetName": "푸드트럭 모듈", "defaultOptionTypes": ["LPG", "버너", "싱크대", "튀김기", "냄비", "냉장고", "전자레인지", "의자", "에어컨", "가스경보기"]},
            {"moduleSetName": "카페 모듈", "defaultOptionTypes": ["테이블", "의자", "커피 머신", "자판기", "냉난방기", "싱크대"]},
            {"moduleSetName": "스포츠 모듈", "defaultOptionTypes": ["스크린 골프", "탁구", "보드게임"]},
            {"moduleSetName": "게임 모듈", "defaultOptionTypes": ["대형모니터", "테이블", "배터리", "게임기", "냉난방기"]},
            {"moduleSetName": "영화관 모듈", "defaultOptionTypes": ["대형모니터", "리클라이닝 의자", "테이블", "냉난방기", "배터리"]},
        ]

        dummy_module_sets = []
        for i, module_set in enumerate(module_set_data):
            all_features = []
            for option_name in module_set["defaultOptionTypes"]:
                option_type = next(
                    (opt for opt in option_type_data if opt["optionTypeName"] == option_name),
                    None
                )
                if option_type and option_type["displayFeatures"]:
                    all_features.extend(option_type["displayFeatures"])
            unique_features = list(set(all_features))
            dummy_module_sets.append({
                "module_set_id": i,
                "module_set_name": module_set["moduleSetName"],
                "description": fake.text(),
                "module_set_images": fake.image_url(),
                "module_set_features": ", ".join(unique_features),
                "base_price": random.randint(1000, 5000),
                "created_at": base_date,
                "updated_at": base_date,
                "created_by": 1,
                "updated_by": 1,
            })
        session.add_all([ModuleSet(**module_set) for module_set in dummy_module_sets])

        # 📌 모듈 세트 옵션 타입 데이터 삽입
        dummy_module_set_option_types = []
        for module_set in module_set_data:
            module_set_id = next(ms["module_set_id"] for ms in dummy_module_sets 
                                if ms["module_set_name"] == module_set["moduleSetName"])
            for option_name in module_set["defaultOptionTypes"]:
                option_type_id = next(
                    (opt_type["option_type_id"] for opt_type in dummy_option_types 
                     if opt_type["option_type_name"] == option_name),
                    None
                )
                if option_type_id is not None:
                    dummy_module_set_option_types.append({
                        "module_set_id": module_set_id,
                        "option_type_id": option_type_id,
                        "option_quantity": 1
                    })
        session.add_all([ModuleSetOptionTypes(**module_set_option_type) for module_set_option_type in dummy_module_set_option_types])

        session.commit()
        print("✅ Seed Data Inserted Successfully!")
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting seed data: {e}")
        # 필요 시 파일 삭제 로직
        if os.path.exists("database.db"):
            os.remove("database.db")
            print("🗑️ database.db 파일이 삭제되었습니다.")
