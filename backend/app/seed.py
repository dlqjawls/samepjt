# app/seeder.py

from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import json
import os
from typing import List
from faker import Faker
from sqlmodel import Session, select
import logging

from app.db.models import (
    Role, ItemStatus, ItemType, ModuleType,
    MaintenanceStatus, UsageStatus, RentStatus, VideoType,
    PaymentStatus, PaymentMethod,
    User, Vehicle, Module, OptionType, Option,
    ModuleSet, ModuleSetOptionTypes
)
from app.db.models.maintenance_history import MaintenanceHistory
from app.utils.bcrypt import hash_password

from app.db.models.rent_history import RentHistory
from app.db.models.usage_history import UsageHistory
from app.utils.lut_constants import ItemType as ItemTypeLUT, UsageStatus as UsageStatusLUT

fake = Faker()
logging.getLogger("faker").setLevel(logging.WARNING)


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
        base_date = datetime(2024, 7, 1)
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
                vehicle_id=1,
                vin="PBVVINNUMBER00001",
                vehicle_number="PBV-00001",
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
            ),      
            Vehicle(
                vehicle_id=2,
                vin="PBVVINNUMBER00002",
                vehicle_number="PBV-00002",
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
        ]
        session.add_all(dummy_vehicles)

        # 📌 모듈 데이터 삽입
        dummy_modules = [
            Module(
                module_id=1,
                module_nfc_tag_id="043F8E6A6C1D90",  # 14자리 16진수 생성 (7바이트)
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
            ),
            Module(
                module_id=2,
                module_nfc_tag_id="043F926A6C1D90",  # 14자리 16진수 생성 (7바이트)
                module_type_id=2,
                item_status_id=2,
                last_maintenance_at=base_date,
                next_maintenance_at=base_date,
                current_location=json.dumps({"x": 0, "y": 0}),
                created_at=base_date,
                created_by=1,
                updated_at=base_date,
                updated_by=1,
                deleted_at=None
            )
        ]
        session.add_all(dummy_modules)

        dummy_option_types = [
            OptionType(
                option_type_id=1,
                option_type_name="TV",
                option_type_size="1x1",
                option_type_cost=3000,
                description="벽걸이형 TV 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/1/1_TV.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=2,
                option_type_name="소형 테이블",
                option_type_size="1x1",
                option_type_cost=2000,
                description="소형 테이블 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/2/2_%ED%85%8C%EC%9D%B4%EB%B8%94.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=3,
                option_type_name="침대",
                option_type_size="1x1",
                option_type_cost=5000,
                description="소형 침대 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/3/3_%EC%B9%A8%EB%8C%80.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=4,
                option_type_name="냉장고",
                option_type_size="1x1",
                option_type_cost=3000,
                description="냉장고 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/4/4_%EB%83%89%EC%9E%A5%EA%B3%A0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=5,
                option_type_name="옷장",
                option_type_size="1x1",
                option_type_cost=2000,
                description="옷장 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/5/5_%EC%98%B7%EC%9E%A5.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=6,
                option_type_name="수납장",
                option_type_size="1x1",
                option_type_cost=1000,
                description="소형 수납장 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/6/6_%EC%88%98%EB%82%A9%EC%9E%A5.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=7,
                option_type_name="싱크대",
                option_type_size="1x1",
                option_type_cost=2000,
                description="싱크대 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/7/7_%EC%8B%B1%ED%81%AC%EB%8C%80.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=8,
                option_type_name="세탁기",
                option_type_size="1x1",
                option_type_cost=3000,
                description="세탁기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/8/8_%EC%84%B8%ED%83%81%EA%B8%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=9,
                option_type_name="인덕션",
                option_type_size="1x1",
                option_type_cost=2000,
                description="요리용 인덕션 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/9/9_%EC%9D%B8%EB%8D%95%EC%85%98.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=10,
                option_type_name="후드",
                option_type_size="1x1",
                option_type_cost=2000,
                description="요리용 후드 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/10/10_%ED%9B%84%EB%93%9C.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=11,
                option_type_name="세면대",
                option_type_size="1x1",
                option_type_cost=3000,
                description="세면대 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/11/1_%EC%84%B8%EB%A9%B4%EB%8C%80.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=12,
                option_type_name="거울",
                option_type_size="1x1",
                option_type_cost=1000,
                description="벽걸이형 거울 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/12/2_%EA%B1%B0%EC%9A%B8.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=13,
                option_type_name="쓰레기통",
                option_type_size="1x1",
                option_type_cost=1000,
                description="소형 쓰레기통 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/13/3_%EC%93%B0%EB%A0%88%EA%B8%B0%ED%86%B5.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=14,
                option_type_name="양변기",
                option_type_size="1x1",
                option_type_cost=3000,
                description="양변기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/14/4_%EC%96%91%EB%B3%80%EA%B8%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),            
            OptionType(
                option_type_id=15,
                option_type_name="남성용 소변기",
                option_type_size="1x1",
                option_type_cost=2000,
                description="남성용 소변기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/15/5_%EB%82%A8%EC%84%B1%EC%86%8C%EB%B3%80%EA%B8%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=16,
                option_type_name="수전",
                option_type_size="1x1",
                option_type_cost=1000,
                description="수전 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/16/6_%EC%88%98%EC%A0%84.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=17,
                option_type_name="대형그릇",
                option_type_size="1x1",
                option_type_cost=1000,
                description="대형 그릇 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/17/6_%EB%8C%80%ED%98%95%EA%B7%B8%EB%A6%87.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=18,
                option_type_name="가스레인지",
                option_type_size="1x1",
                option_type_cost=2000,
                description="조리용 가스레인지 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/18/8_%EA%B0%80%EC%8A%A4%EB%A0%88%EC%9D%B8%EC%A7%80.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=19,
                option_type_name="에어컨",
                option_type_size="1x1",
                option_type_cost=3000,
                description="에어컨 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/19/1_%EC%97%90%EC%96%B4%EC%BB%A8.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=20,
                option_type_name="대형 냄비",
                option_type_size="1x1",
                option_type_cost=2000,
                description="대형 냄비 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/20/3_%EB%8C%80%ED%98%95%EB%83%84%EB%B9%84.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=21,
                option_type_name="중형 냄비",
                option_type_size="1x1",
                option_type_cost=1000,
                description="중형 냄비 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/21/4_%EC%A4%91%ED%98%95%EB%83%84%EB%B9%84.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=22,
                option_type_name="소형 냄비",
                option_type_size="1x1",
                option_type_cost=1000,
                description="소형 냄비 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/22/5_%EC%86%8C%ED%98%95%EB%83%84%EB%B9%84.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=23,
                option_type_name="가판대",
                option_type_size="1x1",
                option_type_cost=2000,
                description="가판대 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/23/10_%EA%B0%80%ED%8C%90%EB%8C%80.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=24,
                option_type_name="커피 머신",
                option_type_size="1x1",
                option_type_cost=3000,
                description="커피 머신 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/24/2_%EC%BB%A4%ED%94%BC%EB%A8%B8%EC%8B%A0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=25,
                option_type_name="대형 테이블",
                option_type_size="1x1",
                option_type_cost=3000,
                description="대형 테이블 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/25/3_%EB%8C%80%ED%98%95%ED%83%81%EC%9E%90.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=26,
                option_type_name="포스기",
                option_type_size="1x1",
                option_type_cost=3000,
                description="포스기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/26/6_%ED%8F%AC%EC%8A%A4%EA%B8%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=27,
                option_type_name="스크린골프용 스크린",
                option_type_size="3x1",
                option_type_cost=5000,
                description="스크린골프용 스크린 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/27/1_%EC%8A%A4%ED%81%AC%EB%A6%B0%EA%B3%A8%ED%94%84%EC%9A%A9_%EC%8A%A4%ED%81%AC%EB%A6%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=28,
                option_type_name="골프채",
                option_type_size="1x1",
                option_type_cost=2000,
                description="골프채 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/28/2_%EA%B3%A8%ED%94%84%EC%B1%84.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=29,
                option_type_name="골프채 거치대",
                option_type_size="1x1",
                option_type_cost=3000,
                description="골프채 거치대 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/29/3_%EA%B3%A8%ED%94%84%EC%B1%84_%EA%B1%B0%EC%B9%98%EB%8C%80.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=30,
                option_type_name="골프공",
                option_type_size="1x1",
                option_type_cost=1000,
                description="골프공 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/30/4_%EA%B3%A8%ED%94%84%EA%B3%B5.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=31,
                option_type_name="골프 카펫",
                option_type_size="1x1",
                option_type_cost=2000,
                description="골프 카펫 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/31/5_%EA%B3%A8%ED%94%84%EC%B9%B4%ED%8E%AB.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=32,
                option_type_name="스코어 스크린",
                option_type_size="1x1",
                option_type_cost=4000,
                description="스코어 스크린 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/32/6_%EC%8A%A4%EC%BD%94%EC%96%B4_%EC%8A%A4%ED%81%AC%EB%A6%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=33,
                option_type_name="TV 다이",
                option_type_size="3x1",
                option_type_cost=2000,
                description="TV 다이 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/33/2_%EB%8B%A4%EC%9D%B4.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=34,
                option_type_name="플레이스테이션",
                option_type_size="1x1",
                option_type_cost=3000,
                description="플레이스테이션 게임기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/34/3_%EA%B2%8C%EC%9E%84%EA%B8%B01.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=35,
                option_type_name="닌텐도",
                option_type_size="1x1",
                option_type_cost=3000,
                description="닌텐도 게임기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/35/4_%EA%B2%8C%EC%9E%84%EA%B8%B02.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=36,
                option_type_name="중형 테이블",
                option_type_size="2x1",
                option_type_cost=2000,
                description="중형 테이블 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/36/6_%EC%A4%91%EA%B0%84_%ED%85%8C%EC%9D%B4%EB%B8%94.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=37,
                option_type_name="소파",
                option_type_size="1x1",
                option_type_cost=3000,
                description="소파 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/37/7_%EC%86%8C%ED%8C%8C.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=38,
                option_type_name="리클라이닝 소파",
                option_type_size="1x1",
                option_type_cost=4000,
                description="리클라이닝 소파 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/38/6_%EB%A6%AC%ED%81%B4%EB%9D%BC%EC%9D%B4%EB%8B%9D_%EC%86%8C%ED%8C%8C.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=39,
                option_type_name="벽걸이 스피커",
                option_type_size="1x1",
                option_type_cost=2000,
                description="벽걸이 스피커 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/39/1_%EB%B2%BD%EA%B1%B8%EC%9D%B4_%EC%8A%A4%ED%94%BC%EC%BB%A4.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=40,
                option_type_name="영사기",
                option_type_size="1x1",
                option_type_cost=5000,
                description="영사기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/40/2_%EC%98%81%EC%82%AC%EA%B8%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=41,
                option_type_name="스탠드 스피커",
                option_type_size="1x1",
                option_type_cost=3000,
                description="스탠드 스피커 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/41/4_%EC%8A%A4%ED%94%BC%EC%BB%A4.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=42,
                option_type_name="스크린",
                option_type_size="3X1",
                option_type_cost=5000,
                description="스크린 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/42/5_%EC%8A%A4%ED%81%AC%EB%A6%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=43,
                option_type_name="냉동용 강력 에어컨",
                option_type_size="1x1",
                option_type_cost=10000,
                description="-18C까지 냉동이 가능한 강력 에어컨 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/43/1_%EB%83%89%EB%8F%99%EC%9A%A9_%EA%B0%95%EB%A0%A5_%EC%97%90%EC%96%B4%EC%BB%A8.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=44,
                option_type_name="건조기",
                option_type_size="1x1",
                option_type_cost=3000,
                description="건조기 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/44/3_%EA%B1%B4%EC%A1%B0%EA%B8%B0.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            ),
            OptionType(
                option_type_id=45,
                option_type_name="의자",
                option_type_size="1x1",
                option_type_cost=1000,
                description="의자 입니다",
                option_type_images="https://moducar.s3.ap-northeast-2.amazonaws.com/optiontype/45/6_%EC%9D%98%EC%9E%90.JPG",
                option_type_features="",
                created_at=base_date,
                updated_at=base_date,
                created_by=1,
                updated_by=1
            )
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
                module_set_name="캠핑 모듈",
                description="캠핑용 모듈 세트입니다.",
                module_set_images="https://moducar.s3.amazonaws.com/moduletype/3/3.JPG",
                module_set_features="",  
                module_type_id=2,
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
                module_set_id=8,
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
        dummy_module_set_option_types= [
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=1,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=2,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=3,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=4,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=5,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=6,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=7,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=8,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=9,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=3,
                option_type_id=10,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=4,
                option_type_id=11,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=4,
                option_type_id=12,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=4,
                option_type_id=13,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=4,
                option_type_id=14,
                option_quantity=3
            ),
            ModuleSetOptionTypes(
                module_set_id=4,
                option_type_id=15,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=4,
                option_type_id=16,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=19,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=1,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=20,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=21,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=22,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=17,
                option_quantity=3
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=7,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=18,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=4,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=5,
                option_type_id=23,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=6,
                option_type_id=1,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=6,
                option_type_id=24,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=6,
                option_type_id=25,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=6,
                option_type_id=26,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=6,
                option_type_id=2,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=6,
                option_type_id=37,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=7,
                option_type_id=27,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=7,
                option_type_id=28,
                option_quantity=5
            ),
            ModuleSetOptionTypes(
                module_set_id=7,
                option_type_id=29,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=7,
                option_type_id=3.,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=7,
                option_type_id=31,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=7,
                option_type_id=32,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=1,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=33,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=34,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=35,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=36,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=37,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=8,
                option_type_id=19,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=9,
                option_type_id=39,
                option_quantity=3
            ),
            ModuleSetOptionTypes(
                module_set_id=9,
                option_type_id=40,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=9,
                option_type_id=41,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=9,
                option_type_id=42,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=9,
                option_type_id=2,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=9,
                option_type_id=38,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=10,
                option_type_id=43,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=11,
                option_type_id=8,
                option_quantity=3
            ),
            ModuleSetOptionTypes(
                module_set_id=11,
                option_type_id=44,
                option_quantity=3
            ),
            ModuleSetOptionTypes(
                module_set_id=11,
                option_type_id=1,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=11,
                option_type_id=19,
                option_quantity=1
            ),
            ModuleSetOptionTypes(
                module_set_id=11,
                option_type_id=45,
                option_quantity=2
            ),
            ModuleSetOptionTypes(
                module_set_id=11,
                option_type_id=2,
                option_quantity=1
            )
        ]
      
        session.add_all(dummy_module_set_option_types)
        session.commit()
        print("✅ Seed Data Inserted Successfully!")
        
        
        # 📌 대여 및 사용 기록 생성
        for _ in range(100):
            start_date = fake.date_time_between(start_date="-120d", end_date="-1d")
            end_date = start_date + timedelta(hours=random.randint(1, 24))
            create_dummy_rent_and_usage(session, start_date, end_date)  
            
        # 📌 유지보수 기록 생성
        for _ in range(10):
            module_id = random.randint(1, 2)
            start_date = fake.date_time_between(start_date="-120d", end_date="-1d")
            end_date = start_date + timedelta(hours=random.randint(1, 24))
            create_dummy_maintenance(session, start_date, end_date)
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting seed data: {e}")
        # 필요 시 파일 삭제 로직
        if os.path.exists("database.db"):
            os.remove("database.db")
            print("🗑️ database.db 파일이 삭제되었습니다.")

def create_dummy_maintenance(session: Session, start_date: datetime, end_date: datetime) -> None: 
    """주어진 모듈 ID와 날짜로 유지보수 기록을 생성하는 함수"""
    
    total_seconds = int((end_date - start_date).total_seconds())
    maintenance_status_id = 3
    
    # 유지보수 기록 생성
    maintenance_history = MaintenanceHistory(
        item_id=random.randint(1, 2),  # 더미 차량 및 모듈 ID
        item_type_id=random.randint(1, 2),  # 더미 아이템 유형 ID'
        issue="유지보수",
        cost=random.randint(100, 500)*100,
        maintenance_status_id=maintenance_status_id,
        scheduled_at=start_date,
        completed_at=end_date,
        created_at=start_date,
        created_by=1,
        updated_at=end_date,
        updated_by=1
    )
    session.add(maintenance_history)
    session.commit()


def create_dummy_rent_and_usage(session: Session, start_date: datetime, end_date: datetime) -> None:
    """주어진 시작일과 마감일로 대여 및 사용 기록을 생성하는 함수"""

    total_seconds = int((end_date - start_date).total_seconds())

    # 대여 시작일과 마감일 설정
    rent_start = start_date 
    rent_end = end_date
    # 예시 비용 계산 (최소 1시간 단위 요금 적용)
    hours = max((rent_end - rent_start).total_seconds() / 3600, 1)
    cost = int(10000 * hours)
    
    # 대여 기록 생성 (예를 들어, user_pk=1, dummy 위치 정보 사용)
    rent_history = RentHistory(
        user_pk=1,
        departure_location='{"x": 0, "y": 0}',
        arrival_location='{"x": 1, "y": 1}',
        cost=cost,
        mileage=random.randint(0, 100),
        rent_status_id=2,  # 완료된 상태 예시
        rent_start_date=rent_start,
        rent_end_date=rent_end,
        created_at=rent_start,
        updated_at=rent_end
    )
    session.add(rent_history)
    session.flush()  # rent_id 할당
    
    # 사용 기록 생성 - 차량
    usage_vehicle = UsageHistory(
        rent_id=rent_history.rent_id,
        item_id=random.randint(1, 2),  # 더미 차량 ID
        item_type_id=ItemTypeLUT.VEHICLE.ID,
        usage_status_id=UsageStatusLUT.COMPLETED.ID,
        created_at=rent_start,
        updated_at=rent_end
    )
    session.add(usage_vehicle)
    
    # 사용 기록 생성 - 모듈
    usage_module = UsageHistory(
        rent_id=rent_history.rent_id,
        item_id=random.randint(1, 2),  # 더미 모듈 ID
        item_type_id=ItemTypeLUT.MODULE.ID,
        usage_status_id=UsageStatusLUT.COMPLETED.ID,
        created_at=rent_start,
        updated_at=rent_end
    )
    session.add(usage_module)
    
    # 사용 기록 생성 - 옵션: 0~10개의 옵션 기록을 생성
    # Option 테이블에서 모든 옵션 id를 조회 
    option_ids = [opt.option_id for opt in session.exec(select(Option)).all()]
    num_options = random.randint(0, 10)
    for _ in range(num_options):
        usage_option = UsageHistory(
            rent_id=rent_history.rent_id,
            item_id=random.choice(option_ids),
            item_type_id=ItemTypeLUT.OPTION.ID,
            usage_status_id=UsageStatusLUT.COMPLETED.ID,
            created_at=rent_start,
            updated_at=rent_end
        )
        session.add(usage_option)
        
    session.commit()