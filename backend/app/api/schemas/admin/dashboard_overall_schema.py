from pydantic import BaseModel
from typing import List
from app.api.schemas.common import ResponseBase

class TopCards(BaseModel):
    todayRentedVehicles: int
    currentlyRentingVehicles: int
    todayExpectedReturnVehicles: int

class ChartItem(BaseModel):
    state: str
    count: int
    ratio: float  # 소수점 첫째자리에서 올림한 값

class StateCharts(BaseModel):
    vehicleStates: List[ChartItem]
    moduleStates: List[ChartItem]
    optionStates: List[ChartItem]

class RentalCountItem(BaseModel):
    date: str
    count: int

class MaintenanceCostItem(BaseModel):
    month: str
    cost: float

class SalesStatistics(BaseModel):
    rentalCountsByDate: List[RentalCountItem]
    maintenanceCostByMonth: List[MaintenanceCostItem]

class Preferences(BaseModel):
    moduleRentalCount: int
    optionRentalCount: int

class DashboardData(BaseModel):
    topCards: TopCards
    stateCharts: StateCharts
    salesStatistics: SalesStatistics
    preferences: Preferences

class DashboardOverallResponse(ResponseBase[DashboardData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Dashboard data retrieved successfully",
                "data": {
                    "topCards": {
                        "todayRentedVehicles": 15,
                        "currentlyRentingVehicles": 10,
                        "todayExpectedReturnVehicles": 5
                    },
                    "stateCharts": {
                        "vehicleStates": [
                            {"state": "Available", "count": 20, "ratio": 50.0},
                            {"state": "Rented", "count": 20, "ratio": 50.0}
                        ],
                        "moduleStates": [
                            {"state": "Active", "count": 30, "ratio": 75.0},
                            {"state": "Maintenance", "count": 10, "ratio": 25.0}
                        ],
                        "optionStates": [
                            {"state": "Active", "count": 40, "ratio": 80.0},
                            {"state": "Maintenance", "count": 10, "ratio": 20.0}
                        ]
                    },
                    "salesStatistics": {
                        "rentalCountsByDate": [
                            {"date": "2025-06-01", "count": 5},
                            {"date": "2025-06-02", "count": 8}
                        ],
                        "maintenanceCostByMonth": [
                            {"month": "2025-06", "cost": 2000.0},
                            {"month": "2025-07", "cost": 1500.0}
                        ]
                    },
                    "preferences": {
                        "moduleRentalCount": 18,
                        "optionRentalCount": 12
                    }
                }
            }
        } 