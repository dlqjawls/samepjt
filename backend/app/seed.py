# app/seeder.py

from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import json
import os
from typing import List
from faker import Faker
from sqlmodel import Session
import logging

from app.db.models import (
    Role, ItemStatus, ItemType, ModuleType,
    MaintenanceStatus, UsageStatus, RentStatus, VideoType,
    PaymentStatus, PaymentMethod,
    User, Vehicle, Module, OptionType, Option,
    ModuleSet, ModuleSetOptionTypes
)
from app.utils.bcrypt import hash_password

fake = Faker()
logging.getLogger("faker").setLevel(logging.WARNING)

@dataclass
class OptionTypeDefinition:
    name: str
    display_features: List[str]
    description: str

@dataclass
class ModuleSetDefinition:
    name: str
    default_option_types: List[str]

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
            ModuleType(module_type_id=1, module_type_name="small", module_type_size="3x3", module_type_cost=5000),
            ModuleType(module_type_id=2, module_type_name="medium", module_type_size="4x4", module_type_cost=10000),
            ModuleType(module_type_id=3, module_type_name="large", module_type_size="5x5", module_type_cost=15000)
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
            PaymentStatus(payment_status_id=1, payment_status_name="pending"),
            PaymentStatus(payment_status_id=2, payment_status_name="completed"),
            PaymentStatus(payment_status_id=3, payment_status_name="failed"),
            PaymentStatus(payment_status_id=4, payment_status_name="refunded")
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
        base_date = datetime(2025, 1, 1)
        dummy_users = [
            User(
                user_pk=1,
                user_id="admin",
                user_password=hash_password("admin123"),
                user_email="admin@example.com",
                user_name="Administrator",
                user_phone_num="010-0000-0000",
                user_address="Seoul, Korea",
                role_id=1,
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            ),
            User(
                user_pk=2,
                user_id="semi", 
                user_password=hash_password("semi123"),
                user_email="semi@example.com",
                user_name="Semi",
                user_phone_num="010-1111-1111",
                user_address="Busan, Korea",
                role_id=2,
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            ),
            User(
                user_pk=3,
                user_id="user",
                user_password=hash_password("user123"),
                user_email="user@example.com",
                user_name="Regular User",
                user_phone_num="010-2222-2222",
                user_address="Incheon, Korea",
                role_id=3,
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            ),
            User(
                user_pk=4,
                user_id="master",
                user_password=hash_password("master123"),
                user_email="master@example.com",
                user_name="Master",
                user_phone_num="010-3333-3333",
                user_address="Seoul, Korea",
                role_id=1,
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            ),
        ]
        session.add_all(dummy_users)

        # 📌 차량 데이터 삽입
        dummy_vehicles = [
            Vehicle(
                vehicle_id=i,
                vin=f"PBVVINNUMBER0000{i}",
                vehicle_number=f"PBV-0000{i}",
                current_location=json.dumps({"x": 0, "y": 0}),
                mileage=0,
                last_maintenance_at=base_date,
                next_maintenance_at=None,
                item_status_id=2,
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            )
            for i in range(1,3)
        ]
        session.add_all(dummy_vehicles)

        # 📌 모듈 데이터 삽입
        dummy_modules = [
            Module(
                module_id=i,
                module_nfc_tag_id=fake.hexify(text='^^^^^^^^^^^^^^', upper=True),  # 14자리 16진수 생성 (7바이트)
                module_type_id=1,
                item_status_id=2,
                last_maintenance_at=base_date,
                next_maintenance_at=base_date,
                current_location=json.dumps({"x": 0, "y": 0}),
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            ) for i in range(1,3)
        ]
        session.add_all(dummy_modules)

        # 📌 옵션 유형 데이터 삽입
        option_type_definitions = [
        ]

        dummy_option_types = [
            OptionType(
                option_type_id=i+1,
                option_type_name=option_def.name,
                option_type_size=f"{random.randint(1, 3)}x{random.randint(1, 3)}",
                option_type_cost=30000,
                description=option_def.description,
                option_type_images=fake.image_url() + ", " + fake.image_url(),
                option_type_features=", ".join(option_def.display_features),
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            )
            for i, option_def in enumerate(option_type_definitions)
        ]
        session.add_all(dummy_option_types)

        # 📌 옵션 데이터 삽입
        dummy_options = []
        option_count = 3  # 각 옵션 타입당 생성할 옵션 개수
        current_id = 1
        for option_type in dummy_option_types:
            for _ in range(option_count):
                option = Option(
                    option_id=current_id,
                    option_type_id=option_type.option_type_id,
                    item_status_id=2,
                    created_at=base_date,
                    updated_at=base_date,
                    created_by=1,
                    updated_by=1
                )
                dummy_options.append(option)
                current_id += 1
        session.add_all(dummy_options)
        
        
        module_set_definitions = [  ]
        
        # 📌 모듈 세트 데이터 삽입
        dummy_module_sets = [
            ModuleSet(
                module_set_id=1,
                module_set_name="기본 모듈",
                description="옵션이 없는 기본 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/1/1.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=2,
                module_set_name="배송 모듈",
                description="배송용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/2/2.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=3,
                module_set_name="캠핑핑 모듈",
                description="캠핑용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/3/3.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=4,
                module_set_name="화장실 모듈",
                description="화장실용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/4/4.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=5,
                module_set_name="푸드트럭 모듈",
                description="푸드트럭용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/5/5.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=6,
                module_set_name="카페 모듈",
                description="카페용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/6/6.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=7,
                module_set_name="게임 모듈",
                description="게임용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/7/7.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=8,
                module_set_name="스크린골프 모듈",
                description="스크린골프용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/8/8.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=9,
                module_set_name="영화관 모듈",
                description="영화관용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/9/9.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=10,
                module_set_name="냉동 모듈",
                description="냉동용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/10/10.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            ModuleSet(
                module_set_id=11,
                module_set_name="세탁실 모듈",
                description="세탁실용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/11/11.JPG",
                module_set_features="",  
                module_type_id=1,
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
        ]
        session.add_all(dummy_module_sets)

        # 📌 모듈 세트 옵션 타입 데이터 삽입
        dummy_module_set_option_types = []
        current_id = 1
        
        # Dictionary to map option type names to their IDs
        option_type_name_to_id = {opt.option_type_name: opt.option_type_id for opt in dummy_option_types}
        
        for i, module_set_def in enumerate(module_set_definitions):
            module_set_id = i + 1  # module_set_id는 1부터 시작
            for option_type_name in module_set_def.default_option_types:
                if option_type_name in option_type_name_to_id:
                    option_type_id = option_type_name_to_id[option_type_name]
                    dummy_module_set_option_types.append(
                        ModuleSetOptionTypes(
                            module_set_id=module_set_id,
                            option_type_id=option_type_id,
                            option_quantity=1
                        )
                    )
                    current_id += 1

        session.add_all(dummy_module_set_option_types)
        session.commit()
        print("✅ Seed Data Inserted Successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting seed data: {e}")
        # 필요 시 파일 삭제 로직
        if os.path.exists("database.db"):
            os.remove("database.db")
            print("🗑️ database.db 파일이 삭제되었습니다.")