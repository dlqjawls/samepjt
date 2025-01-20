from faker import Faker
from datetime import datetime
import random

fake = Faker()

# 더미 사용자 데이터 생성
dummy_users = [
    {
        "userPK": i,
        "userId": fake.user_name(),
        "userPassword": fake.password(),
        "userEmail": fake.email(),
        "userName": fake.name(),
        "userPhoneNum": fake.phone_number(),
        "userAddress": fake.address(),
    }
    for i in range(5)
]

# 더미 차량 데이터 생성
dummy_vehicles = [
    {
        "vehicleId": i,
        "vin": fake.uuid4(),
        "vehicleNumber": f"PBV-{random.randint(1000, 9999)}",
        "departurePoint": {"x": fake.latitude(), "y": fake.longitude()},
        "status": random.choice(["active", "maintenance", "inactive"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1, 6)
]


# 더미 모듈 데이터 생성
dummy_modules = [
    {
        "moduleId": i,
        "moduleNfcTagId": fake.uuid4(),
        "moduleType": random.choice(["default", "extra"]),
        "moduleSize": f"{random.randint(10, 50)}x{random.randint(10, 50)}",
        "moduleCost": random.randint(1000, 5000),
        "status": random.choice(["active", "maintenance", "inactive"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1, 6)
]

# 더미 옵션 데이터 생성
dummy_options = [
    {
        "optionId": i,
        "optionName": fake.word(),
        "optionType": random.choice(["extra-seating", "kitchen", "solar-charging"]),
        "optionSize": f"{random.randint(1, 5)}x{random.randint(1, 5)}",
        "optionCost": random.randint(500, 2000),
        "status": random.choice(["active", "maintenance", "inactive"]),
        "stockQuantity": random.randint(0, 20),
        "imgUrls": [fake.image_url() for _ in range(3)],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1, 6)
]

dummy_module_sets = [
    {
        "moduleSetId": i,
        "moduleSetName": fake.word(),
        "description": fake.sentence(),
        "totalCost": random.randint(1000, 5000),
        "imgsUrls": [fake.image_url() for _ in range(3)],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(1, 6)
]

dummy_module_set_options = [
    {
        "moduleSetId": i,
        "optionId": random.randint(1, 6),
        "quantity": random.randint(1, 3),
    }
    for i in range(1, 6)
]

dummy_vehicles_maintenance = [
    {
        "maintenanceId": i,
        "vehicleId": i,
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "cost": random.randint(100, 500),
        "status": random.choice(["pending", "completed", "in-progress"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(6, 11)
]

dummy_module_maintenance = [
    {
        "maintenanceId": i,
        "moduleId": i,
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "rentId": random.randint(1, 5),
        "cost": random.randint(100, 500),
        "status": random.choice(["pending", "completed", "in-progress"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(6, 11)
]

dummy_option_maintenance = [
    {
        "maintenanceId": i,
        "optionId": i,
        "issue": fake.sentence(),
        "maintenanceDate": datetime.now().isoformat(),
        "optionMaintenanceCost": random.randint(100, 500),
        "status": random.choice(["pending", "completed", "in-progress"]),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    for i in range(6, 11)
]

# 더미 대여 기록 생성
dummy_rent_history = [
    {
        "rentId": i,
        "userPK": random.randint(1, 5),
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
    for i in range(1, 6)
]

dummy_vehicles_usage_history = [
  {
    "vehicleUsageId": i,
    "vehicleId": random.randint(1, 5),
    "rentId": i,
    "usage_start":  datetime.now().isoformat(),
    "usage_end": datetime.now().isoformat(),
    "status": random.choice(["in-use", "completed"]),
  }
  for i in range(1, 6)
]

dummy_module_usage_history = [
    {
        "moduleUsageId": i,
        "moduleId": random.randint(1, 5),        
        "rentId": i,
        "usage_start":  datetime.now().isoformat(),
        "usage_end": datetime.now().isoformat(),
        "status": random.choice(["in-use", "completed"]),
    }
    for i in range(1, 6)
]

dummy_option_usage_history = [
    {
        "optionUsageId": i,
        "optionId": random.randint(1, 5),
        "rentId": i,
        "quantity": random.randint(1, 3),
        "usage_start":  datetime.now().isoformat(),
        "usage_end": datetime.now().isoformat(),
        "status": random.choice(["in-use", "completed"]),
    }
    for i in range(1, 6)
]

dummy_video_storage = [
    {
        "videoId": i,
        "rentId": i,
        "videoType": random.choice(["module_installation", "autonomous_driving"]),
        "videoUrl": fake.url(),
        "recordedAt": datetime.now().isoformat(),
    }
    for i in range(1, 6)
]

if __name__ == "__main__":
    print(dummy_users)
    print(dummy_vehicles)
    print(dummy_modules)
    print(dummy_options)
    print(dummy_module_sets)
    print(dummy_module_set_options)
    print(dummy_vehicles_maintenance)
    print(dummy_module_maintenance)
    print(dummy_option_maintenance)
    print(dummy_rent_history)
    print(dummy_vehicles_usage_history)
    print(dummy_module_usage_history)
    print(dummy_option_usage_history)
    print(dummy_video_storage)
