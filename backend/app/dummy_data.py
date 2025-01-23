import json
from faker import Faker
from datetime import datetime
import random
from datetime import timedelta

from app.utils.bcrypt import hash_password

fake = Faker()

option_type_data = [
    {"optionTypeName": "침대", "optionType": "default", "optionTypeSize": "2x2", "displayFeatures": [], "description": "푹신한 침대입니다."},
    {"optionTypeName": "테이블", "optionType": "default", "optionTypeSize": "2x2", "displayFeatures": [], "description": "넓은 테이블입니다."},
    {"optionTypeName": "의자", "optionType": "default", "optionTypeSize": "0x0", "displayFeatures": [], "description": "편안한 의자입니다."},
    {"optionTypeName": "냉장고", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "음식을 보관할 수 있습니다."},
    {"optionTypeName": "배터리", "optionType": "extra", "optionTypeSize": "0x0", "displayFeatures": ["배터리 잔여량"], "description": "전력을 공급합니다."},
    {"optionTypeName": "수납장", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "물건을 보관할 수 있습니다."},
    {"optionTypeName": "물탱크", "optionType": "extra", "optionTypeSize": "0x0", "displayFeatures": ["물탱크 잔여량", "폐수량"], "description": "물을 저장합니다."},
    {"optionTypeName": "냉난방기", "optionType": "extra", "optionTypeSize": "0x0", "displayFeatures": ["실내온도"], "description": "실내 온도를 조절합니다."},
    {"optionTypeName": "조명", "optionType": "default", "optionTypeSize": "0x0", "displayFeatures": ["조명세기"], "description": "실내 조명을 제공합니다."},
    {"optionTypeName": "대형모니터", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "대형 화면을 제공합니다."},
    {"optionTypeName": "좌변기", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "좌변기 옵션입니다."},
    {"optionTypeName": "세면대", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "세면대 옵션입니다."},
    {"optionTypeName": "거울", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "거울 옵션입니다."},
    {"optionTypeName": "간이계단", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "간이계단 옵션입니다."},
    {"optionTypeName": "LPG", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "LPG 옵션입니다."},
    {"optionTypeName": "버너", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "버너 옵션입니다."},
    {"optionTypeName": "싱크대", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "싱크대 옵션입니다."},
    {"optionTypeName": "튀김기", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "튀김기 옵션입니다."},
    {"optionTypeName": "냄비", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "냄비 옵션입니다."},
    {"optionTypeName": "전자레인지", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "전자레인지 옵션입니다."},
    {"optionTypeName": "에어컨", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": ["실내온도"], "description": "에어컨 옵션입니다."},
    {"optionTypeName": "커피 머신", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": ["커피머신 잔량"], "description": "커피 머신 옵션입니다."},
    {"optionTypeName": "자판기", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": ["자판기 물품 재고량"], "description": "자판기 옵션입니다."},
    {"optionTypeName": "스크린 골프", "optionType": "extra", "optionTypeSize": "2x2", "displayFeatures": [], "description": "스크린 골프 옵션입니다."},
    {"optionTypeName": "탁구", "optionType": "extra", "optionTypeSize": "2x2", "displayFeatures": [], "description": "탁구 옵션입니다."},
    {"optionTypeName": "보드게임", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "보드게임 옵션입니다."},
    {"optionTypeName": "게임기", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "게임기 옵션입니다."},
    {"optionTypeName": "리클라이닝 의자", "optionType": "extra", "optionTypeSize": "1x1", "displayFeatures": [], "description": "리클라이닝 의자 옵션입니다."},
    {"optionTypeName": "가스경보기", "optionType": "extra", "optionTypeSize": "0x0", "displayFeatures": ["가스경보"], "description": "가스경보기 옵션입니다."},
]

module_set_data = [
    {"moduleSetName": "기본본 모듈", "defaultOptionTypes": ["조명"], "displayFeatures": []},
    {"moduleSetName": "캠핑 모듈", "defaultOptionTypes": ["침대", "테이블", "의자", "냉장고", "배터리", "수납장", "물탱크", "냉난방기", "조명"], "displayFeatures": []},
    {"moduleSetName": "오피스 모듈", "defaultOptionTypes": ["테이블", "의자", "대형모니터", "배터리", "냉장고"], "displayFeatures": ["실내온도", "조명세기", "배터리 잔량"]},
    {"moduleSetName": "화장실 모듈", "defaultOptionTypes": ["좌변기", "세면대", "거울", "간이계단"], "displayFeatures": ["물탱크", "조명세기", "오물처리"]},
    {"moduleSetName": "푸드트럭 모듈", "defaultOptionTypes": ["LPG", "버너", "싱크대", "튀김기", "냄비", "냉장고", "전자레인지", "의자", "에어컨", "가스경보기"], "displayFeatures": ["LPG 양", "물탱크 양", "배터리 잔량", "조명세기", "가스경보기", "가스 ON/OFF 여부"]},
    {"moduleSetName": "카페 모듈", "defaultOptionTypes": ["테이블", "의자", "커피 머신", "자판기", "냉난방기", "싱크대"], "displayFeatures": ["물탱크 양", "커피머신 잔량", "자판기 물품 재고량", "실내온도"]},
    {"moduleSetName": "스포츠 모듈", "defaultOptionTypes": ["스크린 골프", "탁구", "보드게임"], "displayFeatures": ["실내온도", "조명세기"]},
    {"moduleSetName": "게임 모듈", "defaultOptionTypes": ["대형모니터", "테이블", "배터리", "게임기", "냉난방기"], "displayFeatures": ["실내온도", "조명세기", "배터리"]},
    {"moduleSetName": "영화관 모듈", "defaultOptionTypes": ["대형모니터", "리클라이닝 의자", "테이블", "냉난방기", "배터리"], "displayFeatures": ["실내온도", "조명세기", "배터리"]},
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
        "optionTypeSize": option["optionTypeSize"],
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

dummy_module_sets = [
    {
        "moduleSetId": i,
        "moduleSetName": module_set["moduleSetName"],
        "description": fake.text(),
        "moduleSetImages": fake.image_url(),
        "moduleSetFeatures": ", ".join(module_set["displayFeatures"]),
        "basePrice": random.randint(1000, 5000),
        "createdAt": base_date.isoformat(),
        "updatedAt": base_date.isoformat(),
    }
    for i, module_set in enumerate(module_set_data)
]

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
    payment_date = datetime.fromisoformat(rent["startTime"])
    refund_date = None
    refund_amount = 0
    
    if rent["rentStatus"] == "canceled":
        refund_date = payment_date + timedelta(days=1)
        refund_amount = rent["totalCost"]
    
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

def validate_data(
    dummy_users, 
    dummy_admins,
    dummy_vehicles,
    dummy_modules,
    dummy_options,
    dummy_module_sets,
    dummy_module_set_option_types,
    dummy_vehicles_maintenance,
    dummy_module_maintenance,
    dummy_option_maintenance,
    dummy_rent_history,
    dummy_payments,
    dummy_vehicles_usage_history,
    dummy_module_usage_history,
    dummy_option_usage_history,
    dummy_video_storage
):
    errors = []

    # 1) ID 리스트 추출 (참조 대상)
    user_pk_list = [u["userPK"] for u in dummy_users]
    admin_pk_list = [a["adminPK"] for a in dummy_admins]
    vehicle_id_list = [v["vehicleId"] for v in dummy_vehicles]
    module_id_list = [m["moduleId"] for m in dummy_modules]
    option_id_list = [o["optionId"] for o in dummy_options]
    module_set_id_list = [ms["moduleSetId"] for ms in dummy_module_sets]
    rent_id_list = [r["rentId"] for r in dummy_rent_history]

    # 시간 순서 검증
    for rent in dummy_rent_history:
        start_time = datetime.fromisoformat(rent["startTime"])
        end_time = datetime.fromisoformat(rent["endTime"])
        if start_time >= end_time:
            errors.append(f"Invalid time order for rentId {rent['rentId']}")
    
    #  비용 계산 검증
    for rent in dummy_rent_history:
        calculated_total = rent["baseCost"] + rent["additionalCost"]
        if calculated_total != rent["totalCost"]:
            errors.append(f"Invalid cost calculation for rentId {rent['rentId']}")

    # 모듈 세트-옵션 매핑 검증
    module_set_options_map = {}
    for mso in dummy_module_set_option_types:
        key = mso["moduleSetId"]
        if key not in module_set_options_map:
            module_set_options_map[key] = []
        module_set_options_map[key].append(mso["optionTypeId"])

    for module_set in module_set_data:
        # 모듈 세트 ID 찾기
        module_set_id = next(
            (ms["moduleSetId"] for ms in dummy_module_sets if ms["moduleSetName"] == module_set["moduleSetName"]),
            None
        )

        if module_set_id is None:
            errors.append(f"❌ 모듈 세트 '{module_set['moduleSetName']}'에 대한 moduleSetId가 존재하지 않음")
            continue

        mapped_options = module_set_options_map.get(module_set_id, [])

        for option_name in module_set["defaultOptionTypes"]:
            # 올바른 optionId 찾기 (option_type.optionTypeId를 참조)
            option_id = next(
                (opt["optionId"] for opt in dummy_options 
                if dummy_option_types[opt["optionType"]]["optionTypeName"] == option_name),
                None
            )

            if option_id is None:
                errors.append(f"❌ 옵션 '{option_name}'에 해당하는 optionId가 존재하지 않음")
            elif option_id not in mapped_options:
                errors.append(f"❌ 모듈 세트 '{module_set['moduleSetName']}'에 '{option_name}' 옵션이 누락됨 (optionId: {option_id})")


    # 3) vehicles_maintenance 검증
    #   - adminPK, vehicleId 유효성 체크
    for idx, entry in enumerate(dummy_vehicles_maintenance):
        if entry["adminPK"] not in admin_pk_list:
            errors.append(f"[vehicles_maintenance][idx={idx}] 잘못된 adminPK: {entry['adminPK']}")
        if entry["vehicleId"] not in vehicle_id_list:
            errors.append(f"[vehicles_maintenance][idx={idx}] 잘못된 vehicleId: {entry['vehicleId']}")

    # 4) module_maintenance 검증
    #   - adminPK, moduleId 유효성 체크
    for idx, entry in enumerate(dummy_module_maintenance):
        if entry["adminPK"] not in admin_pk_list:
            errors.append(f"[module_maintenance][idx={idx}] 잘못된 adminPK: {entry['adminPK']}")
        if entry["moduleId"] not in module_id_list:
            errors.append(f"[module_maintenance][idx={idx}] 잘못된 moduleId: {entry['moduleId']}")

    # 5) option_maintenance 검증
    #   - adminPK, optionId 유효성 체크
    for idx, entry in enumerate(dummy_option_maintenance):
        if entry["adminPK"] not in admin_pk_list:
            errors.append(f"[option_maintenance][idx={idx}] 잘못된 adminPK: {entry['adminPK']}")
        if entry["optionId"] not in option_id_list:
            errors.append(f"[option_maintenance][idx={idx}] 잘못된 optionId: {entry['optionId']}")

    # 6) rent_history 검증
    #   - userPK가 존재하는지 등
    for idx, entry in enumerate(dummy_rent_history):
        if entry["userPK"] not in user_pk_list:
            errors.append(f"[rent_history][idx={idx}] 잘못된 userPK: {entry['userPK']}")

    # 7) payments 검증
    #   - rentId가 실제 존재하는지
    for idx, entry in enumerate(dummy_payments):
        if entry["rentId"] not in rent_id_list:
            errors.append(f"[payments][idx={idx}] 잘못된 rentId: {entry['rentId']}")

    # 8) vehicles_usage_history 검증
    #   - vehicleId, rentId가 실제 존재하는지
    for idx, entry in enumerate(dummy_vehicles_usage_history):
        if entry["vehicleId"] not in vehicle_id_list:
            errors.append(f"[vehicles_usage_history][idx={idx}] 잘못된 vehicleId: {entry['vehicleId']}")
        if entry["rentId"] not in rent_id_list:
            errors.append(f"[vehicles_usage_history][idx={idx}] 잘못된 rentId: {entry['rentId']}")

    # 9) module_usage_history 검증
    #   - moduleId, rentId
    for idx, entry in enumerate(dummy_module_usage_history):
        if entry["moduleId"] not in module_id_list:
            errors.append(f"[module_usage_history][idx={idx}] 잘못된 moduleId: {entry['moduleId']}")
        if entry["rentId"] not in rent_id_list:
            errors.append(f"[module_usage_history][idx={idx}] 잘못된 rentId: {entry['rentId']}")

    # 10) option_usage_history 검증
    #   - optionId, rentId
    for idx, entry in enumerate(dummy_option_usage_history):
        if entry["optionId"] not in option_id_list:
            errors.append(f"[option_usage_history][idx={idx}] 잘못된 optionId: {entry['optionId']}")
        if entry["rentId"] not in rent_id_list:
            errors.append(f"[option_usage_history][idx={idx}] 잘못된 rentId: {entry['rentId']}")

    # 11) video_storage 검증
    #   - rentId
    for idx, entry in enumerate(dummy_video_storage):
        if entry["rentId"] not in rent_id_list:
            errors.append(f"[video_storage][idx={idx}] 잘못된 rentId: {entry['rentId']}")

    # 결과 리턴
    return errors

if __name__ == "__main__":
    # print(dummy_users)
    # print(dummy_vehicles)
    # # print(dummy_modules)
    # print(dummy_options)
    # print(dummy_option_types)
    # print(dummy_module_sets)
    # print(dummy_module_set_option_types)
    # print(dummy_vehicles_maintenance)
    # print(dummy_module_maintenance)
    # print(dummy_option_maintenance)
    # print(dummy_rent_history)
    # print(dummy_vehicles_usage_history)
    # print(dummy_module_usage_history)
    # print(dummy_option_usage_history)
    # print(dummy_video_storage)

    invalid_entries = [entry for entry in dummy_module_set_option_types if entry["optionTypeId"] == -1]
    if invalid_entries:
        print("❌ 매칭되지 않은 옵션 ID 리스트:", invalid_entries)
    else:
        print("✅ 모든 옵션이 정상적으로 매칭되었습니다.")

    # 검증 로직 호출
    errors = validate_data(
        dummy_users, 
        dummy_admins,
        dummy_vehicles,
        dummy_modules,
        dummy_options,
        dummy_module_sets,
        dummy_module_set_option_types,
        dummy_vehicles_maintenance,
        dummy_module_maintenance,
        dummy_option_maintenance,
        dummy_rent_history,
        dummy_payments,
        dummy_vehicles_usage_history,
        dummy_module_usage_history,
        dummy_option_usage_history,
        dummy_video_storage
    )
    if errors:
        print("\n[데이터 검증 결과] 총", len(errors), "개의 오류가 발견되었습니다.")
        for err in errors:
            print(" -", err)
    else:
        print("\n[데이터 검증 결과] 모든 참조가 정상적입니다.")

    print("✅ 초기 데이터 생성 및 검증 완료!")


    # 데이터 검증을 위한 함수
def validate_option_relationships(dummy_option_types, dummy_options, dummy_module_set_option_types, dummy_module_sets):
    errors = []

    # 1) 옵션 타입 ID 리스트
    option_type_id_list = {opt["optionTypeId"] for opt in dummy_option_types}

    # 2) 옵션 ID 리스트 (옵션 타입과 연결된 옵션)
    option_id_list = {opt["optionId"]: opt["optionType"] for opt in dummy_options}

    # 3) 모듈 세트 - 옵션 타입 관계 검증
    for entry in dummy_module_set_option_types:
        module_set_id = entry["moduleSetId"]
        option_type_id = entry["optionTypeId"]

        if option_type_id not in option_type_id_list:
            errors.append(f"❌ [module_set_option_types] moduleSetId {module_set_id}에 속한 optionTypeId {option_type_id}가 존재하지 않음.")

    # 4) 옵션 - 옵션 타입 관계 검증
    for option_id, option_type_id in option_id_list.items():
        if option_type_id not in option_type_id_list:
            errors.append(f"❌ [options] optionId {option_id}에 연결된 optionTypeId {option_type_id}가 존재하지 않음.")

    # 5) 모듈 세트 - 옵션 매핑이 정확한지 확인
    module_set_option_map = {}
    for entry in dummy_module_set_option_types:
        module_set_id = entry["moduleSetId"]
        option_type_id = entry["optionTypeId"]

        if module_set_id not in module_set_option_map:
            module_set_option_map[module_set_id] = set()
        module_set_option_map[module_set_id].add(option_type_id)

    for module_set in dummy_module_sets:
        module_set_id = module_set["moduleSetId"]
        expected_options = {opt["optionTypeId"] for opt in dummy_module_set_option_types if opt["moduleSetId"] == module_set_id}
        
        if module_set_id in module_set_option_map:
            actual_options = module_set_option_map[module_set_id]
            if expected_options != actual_options:
                errors.append(f"⚠️ [module_sets] moduleSetId {module_set_id}의 옵션 타입이 예상과 다름. (expected={expected_options}, actual={actual_options})")

    return errors

# 검증 실행
errors = validate_option_relationships(dummy_option_types, dummy_options, dummy_module_set_option_types, dummy_module_sets)

# 결과 출력
if errors:
    print("\n[데이터 검증 결과] 총", len(errors), "개의 오류가 발견되었습니다.")
    for err in errors:
        print(" -", err)
else:
    print("\n[데이터 검증 결과] 옵션, 옵션 타입, 모듈 세트 옵션 타입 관계가 정상적입니다. ✅")