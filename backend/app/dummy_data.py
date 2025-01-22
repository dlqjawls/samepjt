from faker import Faker
from datetime import datetime
import random

from app.utils.bcrypt import hash_password

fake = Faker()

option_data = [
    {"optionName": "침대", "optionType": "default", "optionSize": "2x2", "displayFeatures": [], "description": "푹신한 침대입니다."},
    {"optionName": "테이블", "optionType": "default", "optionSize": "2x2", "displayFeatures": [], "description": "넓은 테이블입니다."},
    {"optionName": "의자", "optionType": "default", "optionSize": "0x0", "displayFeatures": [], "description": "편안한 의자입니다."},
    {"optionName": "냉장고", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "음식을 보관할 수 있습니다."},
    {"optionName": "배터리", "optionType": "extra", "optionSize": "0x0", "displayFeatures": ["배터리 잔여량"], "description": "전력을 공급합니다."},
    {"optionName": "수납장", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "물건을 보관할 수 있습니다."},
    {"optionName": "물탱크", "optionType": "extra", "optionSize": "0x0", "displayFeatures": ["물탱크 잔여량", "폐수량"], "description": "물을 저장합니다."},
    {"optionName": "냉난방기", "optionType": "extra", "optionSize": "0x0", "displayFeatures": ["실내온도"], "description": "실내 온도를 조절합니다."},
    {"optionName": "조명", "optionType": "default", "optionSize": "0x0", "displayFeatures": ["조명세기"], "description": "실내 조명을 제공합니다."},
    {"optionName": "대형모니터", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "대형 화면을 제공합니다."},
    {"optionName": "좌변기", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "좌변기 옵션입니다."},
    {"optionName": "세면대", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "세면대 옵션입니다."},
    {"optionName": "거울", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "거울 옵션입니다."},
    {"optionName": "간이계단", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "간이계단 옵션입니다."},
    {"optionName": "LPG", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "LPG 옵션입니다."},
    {"optionName": "버너", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "버너 옵션입니다."},
    {"optionName": "싱크대", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "싱크대 옵션입니다."},
    {"optionName": "튀김기", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "튀김기 옵션입니다."},
    {"optionName": "냄비", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "냄비 옵션입니다."},
    {"optionName": "전자레인지", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "전자레인지 옵션입니다."},
    {"optionName": "에어컨", "optionType": "extra", "optionSize": "1x1", "displayFeatures": ["실내온도"], "description": "에어컨 옵션입니다."},
    {"optionName": "커피 머신", "optionType": "extra", "optionSize": "1x1", "displayFeatures": ["커피머신 잔량"], "description": "커피 머신 옵션입니다."},
    {"optionName": "자판기", "optionType": "extra", "optionSize": "1x1", "displayFeatures": ["자판기 물품 재고량"], "description": "자판기 옵션입니다."},
    {"optionName": "스크린 골프", "optionType": "extra", "optionSize": "2x2", "displayFeatures": [], "description": "스크린 골프 옵션입니다."},
    {"optionName": "탁구", "optionType": "extra", "optionSize": "2x2", "displayFeatures": [], "description": "탁구 옵션입니다."},
    {"optionName": "보드게임", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "보드게임 옵션입니다."},
    {"optionName": "게임기", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "게임기 옵션입니다."},
    {"optionName": "리클라이닝 의자", "optionType": "extra", "optionSize": "1x1", "displayFeatures": [], "description": "리클라이닝 의자 옵션입니다."},
    {"optionName": "가스경보기", "optionType": "extra", "optionSize": "0x0", "displayFeatures": ["가스경보"], "description": "가스경보기 옵션입니다."},
]

module_set_data = [
    {"moduleSetName": "기본본 모듈", "defaultOptions": ["조명"], "displayFeatures": []},
    {"moduleSetName": "캠핑 모듈", "defaultOptions": ["침대", "테이블", "의자", "냉장고", "배터리", "수납장", "물탱크", "냉난방기", "조명"], "displayFeatures": []},
    {"moduleSetName": "오피스 모듈", "defaultOptions": ["테이블", "의자", "대형모니터", "배터리", "냉장고"], "displayFeatures": ["실내온도", "조명세기", "배터리 잔량"]},
    {"moduleSetName": "화장실 모듈", "defaultOptions": ["좌변기", "세면대", "거울", "간이계단"], "displayFeatures": ["물탱크", "조명세기", "오물처리"]},
    {"moduleSetName": "푸드트럭 모듈", "defaultOptions": ["LPG", "버너", "싱크대", "튀김기", "냄비", "냉장고", "전자레인지", "의자", "에어컨", "가스경보기"], "displayFeatures": ["LPG 양", "물탱크 양", "배터리 잔량", "조명세기", "가스경보기", "가스 ON/OFF 여부"]},
    {"moduleSetName": "카페 모듈", "defaultOptions": ["테이블", "의자", "커피 머신", "자판기", "냉난방기", "싱크대"], "displayFeatures": ["물탱크 양", "커피머신 잔량", "자판기 물품 재고량", "실내온도"]},
    {"moduleSetName": "스포츠 모듈", "defaultOptions": ["스크린 골프", "탁구", "보드게임"], "displayFeatures": ["실내온도", "조명세기"]},
    {"moduleSetName": "게임 모듈", "defaultOptions": ["대형모니터", "테이블", "배터리", "게임기", "냉난방기"], "displayFeatures": ["실내온도", "조명세기", "배터리"]},
    {"moduleSetName": "영화관 모듈", "defaultOptions": ["대형모니터", "리클라이닝 의자", "테이블", "냉난방기", "배터리"], "displayFeatures": ["실내온도", "조명세기", "배터리"]},
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
dummy_vehicles = [
    {
        "vehicleId": 0,
        "vin": fake.uuid4(),
        "vehicleNumber": f"PBV-{random.randint(1000, 9999)}",
        "currentLocation": {"x": 0, "y": 0},
        "status": "inactive",
        "mileage": random.randint(1000, 5000),
        "lastMaintenanceAt": datetime.now().isoformat(),
        "nextMaintenanceAt": datetime.now().isoformat(),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
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
        "status": random.choice(["pending", "completed", "in-progress"]),
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
        "status": random.choice(["active", "maintenance", "inactive"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(3)
]

# 더미 옵션 데이터 생성
dummy_options = [
    {
        "optionId": i,
        "optionName": option["optionName"],
        "optionType": option["optionType"],
        "optionSize": option["optionSize"],
        "optionCost": random.randint(500, 2000),
        "description": option["description"],
        "displayFeatures": option["displayFeatures"],
        "status": "inactive",
        "stockQuantity": random.randint(0, 20),
        "imgUrls": [fake.image_url() for _ in range(3)],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i, option in enumerate(option_data)
]

dummy_module_sets = [
    {
        "moduleSetId": i, 
        "moduleSetName": module["moduleSetName"],
        "description": f"{module['moduleSetName']} 세트 입니다.",
        "totalCost": random.randint(1000, 5000),
        "imgsUrls": [fake.image_url() for _ in range(random.randint(1, 3))],
        "displayFeatures": module["displayFeatures"],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i, module in enumerate(module_set_data)
]

# 모듈 세트 옵션 매핑
dummy_module_set_options = [
    {
        "moduleSetId": module_set["moduleSetId"],
        "optionId": next(
            (opt["optionId"] for opt in dummy_options if opt["optionName"] == option_name),
            -1
        ),
        "quantity": random.randint(1, 3),
    }
    for module_set in dummy_module_sets
    for option_name in next(
        (mod["defaultOptions"] for mod in module_set_data if mod["moduleSetName"] == module_set["moduleSetName"]),
        []
    )
]


dummy_module_maintenance = [
    {
        "maintenanceId": i,
        "moduleId": random.choice(dummy_modules)["moduleId"],
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "rentId": random.randint(1, 5),
        "cost": random.randint(100, 500),
        "status": random.choice(["pending", "completed", "in-progress"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1)
]

dummy_option_maintenance = [
    {
        "maintenanceId": i,
        "optionId": random.choice(dummy_options)["optionId"],
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "optionMaintenanceCost": random.randint(100, 500),
        "status": random.choice(["pending", "completed", "in-progress"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1)
]

# 더미 대여 기록 생성
dummy_rent_history = [
    {
        "rentId": i,
        "userPK": random.choice(dummy_users)["userPK"],
        "autonomousArrivalPoint": {"x": fake.latitude(), "y": fake.longitude()},
        "autonomousDeparturePoint": {"x": fake.latitude(), "y": fake.longitude()},
        "rentStatus": random.choice(["reserved", "in-progress", "completed", "canceled"]),
        "eventType": random.choice(["start", "end"]),
        "startTime": datetime.now().isoformat(),
        "endTime": datetime.now().isoformat(),
        "totalCost": random.randint(100, 500),
        "totalDistance": random.randint(10, 100),
        "statusUpdateAt": datetime.now().isoformat(),
        "createdAt": datetime.now().isoformat(),
    }
    for i in range(1)
] 

dummy_vehicles_usage_history = [
    {
        "vehicleUsageId": i,
        "vehicleId": random.choice(dummy_vehicles)["vehicleId"],
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "usage_start": datetime.now().isoformat(),
        "usage_end": datetime.now().isoformat(),
        "status": random.choice(["in-use", "completed"]),
    }
    for i in range(1)
]

dummy_module_usage_history = [
    {
        "moduleUsageId": i,
        "moduleId": random.choice(dummy_modules)["moduleId"],
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "usage_start": datetime.now().isoformat(),
        "usage_end": datetime.now().isoformat(),
        "status": random.choice(["in-use", "completed"]),
    }
    for i in range(1)
]

dummy_option_usage_history = [
    {
        "optionUsageId": i,
        "optionId": random.choice(dummy_options)["optionId"],
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "quantity": random.randint(1, 3),
        "usage_start": datetime.now().isoformat(),
        "usage_end": datetime.now().isoformat(),
        "status": random.choice(["in-use", "completed"]),
    }
    for i in range(1)
]

dummy_video_storage = [
    {
        "videoId": i,
        "rentId": random.choice(dummy_rent_history)["rentId"],
        "videoType": random.choice(["module_installation", "autonomous_driving"]),
        "videoUrl": fake.url(),
        "recordedAt": datetime.now().isoformat(),
    }
    for i in range(1)
]


if __name__ == "__main__":
    # print(dummy_users)
    # print(dummy_vehicles)
    # print(dummy_modules)
    # print(dummy_options)
    # print(dummy_module_sets)
    # print(dummy_module_set_options)
    print(dummy_vehicles_maintenance)
    print(dummy_module_maintenance)
    print(dummy_option_maintenance)
    print(dummy_rent_history)
    print(dummy_vehicles_usage_history)
    print(dummy_module_usage_history)
    print(dummy_option_usage_history)
    print(dummy_video_storage)

invalid_entries = [entry for entry in dummy_module_set_options if entry["optionId"] == -1]
if invalid_entries:
    print("❌ 매칭되지 않은 옵션 ID 리스트:", invalid_entries)
else:
    print("✅ 모든 옵션이 정상적으로 매칭되었습니다.")

print("✅ 초기 데이터 생성 완료!")
print("✔ dummy_options:", len(dummy_options), "개")
print("✔ dummy_module_sets:", len(dummy_module_sets), "개")
print("✔ dummy_module_set_options:", len(dummy_module_set_options), "개")