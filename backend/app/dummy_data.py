import json
from faker import Faker
from datetime import datetime
import random
from datetime import timedelta

from app.utils.bcrypt import hash_password

fake = Faker()

option_type_data = [
    {"optionTypeName": "침대",   "displayFeatures": [], "description": "푹신한 침대입니다."},
    {"optionTypeName": "테이블", "displayFeatures": [], "description": "넓은 테이블입니다."},
    {"optionTypeName": "의자",   "displayFeatures": [], "description": "편안한 의자입니다."},
    {"optionTypeName": "냉장고",   "displayFeatures": [], "description": "음식을 보관할 수 있습니다."},
    {"optionTypeName": "배터리",  "displayFeatures": ["배터리 잔여량"], "description": "전력을 공급합니다."},
    {"optionTypeName": "수납장",   "displayFeatures": [], "description": "물건을 보관할 수 있습니다."},
    {"optionTypeName": "물탱크",  "displayFeatures": ["물탱크 잔여량", "폐수량"], "description": "물을 저장합니다."},
    {"optionTypeName": "냉난방기", "displayFeatures": ["실내온도"], "description": "실내 온도를 조절합니다."},
    {"optionTypeName": "조명",   "displayFeatures": ["조명세기"], "description": "실내 조명을 제공합니다."},
    {"optionTypeName": "대형모니터", "displayFeatures": [], "description": "대형 화면을 제공합니다."},
    {"optionTypeName": "좌변기", "displayFeatures": [], "description": "좌변기 옵션입니다."},
    {"optionTypeName": "세면대", "displayFeatures": [], "description": "세면대 옵션입니다."},
    {"optionTypeName": "거울",  "displayFeatures": [], "description": "거울 옵션입니다."},
    {"optionTypeName": "간이계단", "displayFeatures": [], "description": "간이계단 옵션입니다."},
    {"optionTypeName": "LPG",  "displayFeatures": [], "description": "LPG 옵션입니다."},
    {"optionTypeName": "버너",  "displayFeatures": [], "description": "버너 옵션입니다."},
    {"optionTypeName": "싱크대", "displayFeatures": [], "description": "싱크대 옵션입니다."},
    {"optionTypeName": "튀김기", "displayFeatures": [], "description": "튀김기 옵션입니다."},
    {"optionTypeName": "냄비", "displayFeatures": [], "description": "냄비 옵션입니다."},
    {"optionTypeName": "전자레인지", "displayFeatures": [], "description": "전자레인지 옵션입니다."},
    {"optionTypeName": "에어컨",  "displayFeatures": ["실내온도"], "description": "에어컨 옵션입니다."},
    {"optionTypeName": "커피 머신",  "displayFeatures": ["커피머신 잔량"], "description": "커피 머신 옵션입니다."},
    {"optionTypeName": "자판기", "displayFeatures": ["자판기 물품 재고량"], "description": "자판기 옵션입니다."},
    {"optionTypeName": "스크린 골프",  "displayFeatures": [], "description": "스크린 골프 옵션입니다."},
    {"optionTypeName": "탁구",  "displayFeatures": [], "description": "탁구 옵션입니다."},
    {"optionTypeName": "보드게임",   "displayFeatures": [], "description": "보드게임 옵션입니다."},
    {"optionTypeName": "게임기", "displayFeatures": [], "description": "게임기 옵션입니다."},
    {"optionTypeName": "리클라이닝 의자", "displayFeatures": [], "description": "리클라이닝 의자 옵션입니다."},
    {"optionTypeName": "가스경보기", "displayFeatures": ["가스경보"], "description": "가스경보기 옵션입니다."},
]

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

# 더미 사용자 데이터 생성
dummy_users = [
    {
        "userPK": 0,
        "userId": "test123",
        "userPassword": hash_password("test123"),
        "userEmail": "test@user.com",
        "userName": "테스트유저",
        "userPhoneNum": "010-1234-5678",
        "userAddress": "서울시 강남구",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
]

dummy_admins = [
    {
        "adminPK": 1,
        "adminId": "admin",
        "adminPassword": hash_password("admin123"),
        "role": "master",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    },
    {
        "adminPK": 2,
        "adminId": "semi",
        "adminPassword": hash_password("semi123"),
        "role": "semi",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
]

# 더미 차량 데이터 생성
base_date = datetime.now()
dummy_vehicles = [
    {
        "vehicleId": 0,
        "vin": fake.uuid4(),
        "vehicleNumber": f"PBV-{random.randint(1000, 9999)}",
        "currentLocation": json.dumps({
            "x": round(random.uniform(35.0, 38.0), 6),  # 한국 위도 범위
            "y": round(random.uniform(126.0, 129.0), 6)  # 한국 경도 범위
        }),
        "status": "inactive",
        "mileage": random.randint(1000, 5000),
        "lastMaintenanceAt": base_date.isoformat(),
        "nextMaintenanceAt": (base_date + timedelta(days=90)).isoformat(),  # 90일 후 정비
        "createdAt": base_date.isoformat(),
        "updatedAt": base_date.isoformat(),
    }
]

dummy_vehicles_maintenance = [
    {
        "maintenanceId": i,
        "adminPK": random.choice(dummy_admins)["adminPK"], 
        "vehicleId": random.choice(dummy_vehicles)["vehicleId"],
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "cost": random.randint(100, 500),
        "status": random.choice(["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
        "completedAt": datetime.now().isoformat(),
        "notes": fake.sentence(),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1)
]

# 더미 모듈 데이터 생성
dummy_modules = [
    {
        "moduleId": i,
        "moduleNfcTagId": fake.uuid4(),
        "moduleType": "default",
        "moduleSize": f"{random.randint(10, 50)}x{random.randint(10, 50)}",
        "moduleCost": random.randint(1000, 5000),
        "status": random.choice(["ACTIVE", "INACTIVE", "MAINTENANCE"]),
        "lastMaintenanceAt" : datetime.now().isoformat(),
        "nextMaintenanceAt" : datetime.now().isoformat(),
        "currentLocation" : json.dumps({"x": 0, "y": 0}),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(3)
]

# 더미 옵션 데이터 생성
dummy_option_types = [
    {
        "optionTypeId": i,
        "optionTypeName": option["optionTypeName"],
        "optionTypeSize": f"{random.randint(1, 3)}x{random.randint(1, 3)}",
        "optionTypeCost": round(random.uniform(10.0, 100.0), 2),
        "description": option["description"],
        "optionTypeImages": fake.image_url(),
        "optionTypeFeatures": ", ".join(option["displayFeatures"]),
        "createdAt": base_date.isoformat(),
        "updatedAt": base_date.isoformat(),
    }
    for i, option in enumerate(option_type_data)
]

dummy_options = [
    {
        "optionId": i,
        "optionType": dummy_option_types[i]["optionTypeId"],
        "status": random.choice(["ACTIVE", "INACTIVE", "MAINTENANCE"]),
        "createdAt": base_date.isoformat(),
        "updatedAt": base_date.isoformat(),
    }
    for i, option in enumerate(option_type_data)
]

# dummy_module_sets 생성 부분 수정
dummy_module_sets = []

for i, module_set in enumerate(module_set_data):
    # 해당 모듈 세트의 모든 옵션 타입의 displayFeatures 수집
    all_features: list[str] = []
    for option_name in module_set["defaultOptionTypes"]:
        # 해당 옵션 이름에 매칭되는 옵션 타입 찾기
        option_type = next(
            (opt for opt in option_type_data if opt["optionTypeName"] == option_name),
            None
        )
        if option_type and option_type["displayFeatures"]:
            all_features.extend(option_type["displayFeatures"])
    
    # 중복 제거를 위해 set으로 변환 후 다시 list로 변환
    unique_features = list(set(all_features))
    
    dummy_module_sets.append({
        "moduleSetId": i,
        "moduleSetName": module_set["moduleSetName"],
        "description": fake.text(),
        "moduleSetImages": fake.image_url(),
        "moduleSetFeatures": ", ".join(unique_features),  # 수집된 unique features 사용
        "basePrice": random.randint(1000, 5000),
        "createdAt": base_date.isoformat(),
        "updatedAt": base_date.isoformat(),
    })

dummy_module_set_option_types = []
for module_set in module_set_data:
    module_set_id = next(ms["moduleSetId"] for ms in dummy_module_sets 
                        if ms["moduleSetName"] == module_set["moduleSetName"])
    
    for option_name in module_set["defaultOptionTypes"]:
        option_type_id = next((opt_type["optionTypeId"] for opt_type in dummy_option_types 
                               if opt_type["optionTypeName"] == option_name), None)
        
        if option_type_id is not None:
            dummy_module_set_option_types.append({
                "moduleSetId": module_set_id,
                "optionTypeId": option_type_id,
                "quantity": 1,
            })

dummy_module_maintenance = [
    {
        "maintenanceId": i,
        "adminPK": random.choice(dummy_admins)["adminPK"],
        "moduleId": random.choice(dummy_modules)["moduleId"],
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "cost": random.randint(100, 500), 
        "status" : random.choice(["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
        "completedAt ": datetime.now().isoformat(),
        "notes": fake.sentence(),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1)
]

dummy_option_maintenance = [
    {
        "maintenanceId": i,
        "adminPK": random.choice(dummy_admins)["adminPK"],
        "optionId": random.choice(dummy_options)["optionId"],
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "cost": random.randint(100, 500),
        "status" : random.choice(["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
        "completedAt ": datetime.now().isoformat(),
        "notes": fake.sentence(),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1)
]

# 더미 대여 기록 생성
dummy_rent_history = []
for i in range(1):
    start_time = base_date + timedelta(days=random.randint(1, 30))
    end_time = start_time + timedelta(hours=random.randint(1, 48))
    base_cost = random.randint(100, 500)
    additional_cost = random.randint(100, 500)
    
    dummy_rent_history.append({
        "rentId": i,
        "userPK": random.choice(dummy_users)["userPK"],
        "departureLocation": json.dumps({
            "x": round(random.uniform(35.0, 38.0), 6),
            "y": round(random.uniform(126.0, 129.0), 6)
        }),
        "arrivalLocation": json.dumps({
            "x": round(random.uniform(35.0, 38.0), 6),
            "y": round(random.uniform(126.0, 129.0), 6)
        }),
        "rentStatus": random.choice(["RESERVED", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "baseCost": base_cost,
        "additionalCost": additional_cost,
        "totalCost": base_cost + additional_cost,
        "totalDistance": random.randint(10, 100),
        "statusUpdatedAt": base_date.isoformat(),
        "createdAt": base_date.isoformat(),
    })

dummy_payments = []
for i, rent in enumerate(dummy_rent_history):
    payment_date = datetime.fromisoformat(str(rent["startTime"]))
    refund_date = None
    refund_amount = 0
    
    if rent["rentStatus"] == "canceled":
        refund_date = payment_date + timedelta(days=1)
        refund_amount = int(rent["totalCost"])
    
    dummy_payments.append({
        "paymentId": i,
        "rentId": rent["rentId"],
        "amount": rent["totalCost"],
        "status": "paid" if rent["rentStatus"] != "canceled" else "refunded",
        "paymentMethod": random.choice(["credit_card", "cash"]),
        "paymentDate": payment_date.isoformat(),
        "refundAmount": refund_amount,
        "refundDate": refund_date.isoformat() if refund_date else None,
        "createdAt": base_date.isoformat(),
        "updatedAt": base_date.isoformat(),
    })

dummy_vehicles_usage_history = [
    {
        "vehicleUsageId": i,
        "vehicleId": random.choice(dummy_vehicles)["vehicleId"],
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "startLocation": fake.address(),
        "endLocation": fake.address(),
        "startTime": datetime.now().isoformat(),
        "endTime": datetime.now().isoformat(),
        "status": random.choice(["RESERVED", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
        "mileage": random.randint(1000, 5000),
    }
    for i in range(1)
]

dummy_module_usage_history = [
    {
        "moduleUsageId": i,
        "moduleId": random.choice(dummy_modules)["moduleId"],
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "startTime": datetime.now().isoformat(),
        "endTime": datetime.now().isoformat(),
        "status": random.choice(["RESERVED", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
    }
    for i in range(1)
]

dummy_option_usage_history = [
    {
        "optionUsageId": i,
        "optionId": random.choice(dummy_options)["optionId"],
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "startTime": datetime.now().isoformat(),
        "endTime": datetime.now().isoformat(),
        "status": random.choice(["RESERVED", "IN_PROGRESS", "COMPLETED", "CANCELED"]),
        "createdAt": datetime.now().isoformat(),
    }
    for i in range(1)
]

dummy_video_storage = [
    {
        "videoId": i,
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "videoType": random.choice(["MODULE_INSTALLATION", "AUTONOMOUS_DRIVING"]),
        "videoUrl": fake.url(),
        "duration": random.randint(1, 100),
        "size": random.randint(1, 100),
        "recordedAt": datetime.now().isoformat(),
        "createdAt": datetime.now().isoformat(),
    }
    for i in range(1)
]
