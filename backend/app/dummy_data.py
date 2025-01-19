from faker import Faker
from datetime import datetime
import random

fake = Faker()

# 더미 사용자 데이터 생성
dummy_users = [
    {
        "userId": fake.user_name(),
        "userPassword": fake.password(),
        "userEmail": fake.email(),
        "userName": fake.name(),
        "userPhoneNum": fake.phone_number(),
        "userAddress": fake.address(),
    }
    for _ in range(5)
]

# 더미 차량 데이터 생성
dummy_vehicles = [
    {
        "vehicleId": i,
        "vin": fake.uuid4(),
        "carNumber": f"PBV-{random.randint(1000, 9999)}",
        "departure_point": fake.address(),
        "status": random.choice(["active", "maintenance", "inactive"]),
    }
    for i in range(1, 6)
]

# 더미 대여 기록 생성
dummy_rentals = [
    {
        "rentId": i,
        "userPK": random.randint(1, 5),
        "autonomousArrivalPoint": {"x": fake.latitude(), "y": fake.longitude()},
        "autonomousDeparturePoint": {"x": fake.latitude(), "y": fake.longitude()},
        "rentStatus": random.choice(["reserved", "in-progress", "completed", "canceled"]),
        "startTime": datetime.now().isoformat(),
        "endTime": datetime.now().isoformat(),
        "totalCost": random.randint(100, 500),
    }
    for i in range(1, 6)
]

# 더미 모듈 데이터 생성
dummy_modules = [
    {
        "moduleId": i,
        "moduleNfcTagId": fake.uuid4(),
        "moduleType": random.choice(["battery", "fridge", "solar-panel"]),
        "moduleSize": f"{random.randint(10, 50)}x{random.randint(10, 50)}",
        "moduleCost": random.randint(1000, 5000),
        "status": random.choice(["active", "maintenance", "inactive"]),
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
        "stockQuantity": random.randint(0, 20),
    }
    for i in range(1, 6)
]

if __name__ == "__main__":
    print("Dummy Users:", dummy_users)
    print("Dummy Vehicles:", dummy_vehicles)
    print("Dummy Rentals:", dummy_rentals)
    print("Dummy Modules:", dummy_modules)
    print("Dummy Options:", dummy_options)
