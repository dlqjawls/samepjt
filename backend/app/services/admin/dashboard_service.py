from datetime import date, datetime, time
import math
from sqlmodel import Session, select, func
from app.db.models.rent_history import RentHistory
from app.db.models.maintenance_history import MaintenanceHistory
from app.db.models.vehicle import Vehicle
from app.db.models.module import Module
from app.db.models.option import Option
from app.db.crud.rent_history import rent_history_crud
from app.db.crud.lut import item_status, item_type
from app.db.models.usage_history import UsageHistory

class DashboardService:
    @staticmethod
    def get_today_rented_vehicles_count(session: Session) -> int:
        # 오늘 날짜의 시작(00:00:00)과 끝(23:59:59)를 계산
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        # RentHistory 모델의 created_at가 오늘인 데이터만 필터링함
        query = select(RentHistory).where(RentHistory.created_at >= start, RentHistory.created_at <= end)
        # paginate() 메서드를 사용하여 총 건수를 얻음 (여기서는 페이지 사이즈를 아주 크게 지정)
        paginated = rent_history_crud.paginate(session, 1, 1000, query)
        return paginated["pagination"]["totalItems"]

    @staticmethod
    def get_currently_renting_vehicles_count(session: Session) -> int:
        # RENTING_STATUS_ID는 현재 대여중인 상태를 나타내는 ID로 가정 (예: 2)
        RENTING_STATUS_ID = 1
        query = select(RentHistory).where(RentHistory.rent_status_id == RENTING_STATUS_ID)
        results = session.exec(query).all()
        return len(results)

    @staticmethod
    def get_today_expected_return_vehicles_count(session: Session) -> int:
        # RentHistory에 expected_return_at 필드가 있다고 가정
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        query = select(RentHistory).where(RentHistory.rent_end_date >= start, RentHistory.rent_end_date <= end)
        results = session.exec(query).all()
        return len(results)

    @staticmethod
    def get_state_chart(query_model, id_field, count_field, session: Session):
        # query_model: Vehicle, Module, Option 모델
        total = session.exec(select(func.count()).select_from(query_model)).one()
        group_query = (
            select(getattr(query_model, "item_status_id"), func.count(count_field))
            .group_by(getattr(query_model, "item_status_id"))
        )
        results = session.exec(group_query).all()
        state_chart = []
        for status_id, cnt in results:
            # item_status CRUD를 통해 상태명을 조회 (예: "Available", "Rented" 등)
            status_obj = item_status.get_by_id(session, status_id)
            ratio = (cnt / total * 100) if total > 0 else 0
            ratio = math.ceil(ratio * 10) / 10  # 소수점 첫째자리에서 올림
            state_chart.append({
                "state": status_obj.item_status_name,
                "count": cnt,
                "ratio": ratio
            })
        return state_chart

    @staticmethod
    def get_vehicle_state_chart(session: Session):
        return DashboardService.get_state_chart(Vehicle, Vehicle.vehicle_id, Vehicle.vehicle_id, session)

    @staticmethod
    def get_module_state_chart(session: Session):
        return DashboardService.get_state_chart(Module, Module.module_id, Module.module_id, session)

    @staticmethod
    def get_option_state_chart(session: Session):
        return DashboardService.get_state_chart(Option, Option.option_id, Option.option_id, session)

    @staticmethod
    def get_rental_counts_by_date(session: Session):
        # 날짜별 대여 횟수를 계산 (SQLite의 경우 func.strftime 사용, 다른 DBMS에선 적절히 수정)
        query = (
            select(func.strftime('%Y-%m-%d', RentHistory.created_at).label("date"), func.count(RentHistory.rent_id))
            .group_by(func.strftime('%Y-%m-%d', RentHistory.created_at))
            .order_by("date")
        )
        results = session.exec(query).all()
        return [{"date": r[0], "count": r[1]} for r in results]

    @staticmethod
    def get_maintenance_cost_by_month(session: Session):
        # 월별 정비 비용 합계를 계산 (SQLite 예시)
        query = (
            select(func.strftime('%Y-%m', MaintenanceHistory.created_at).label("month"), func.sum(MaintenanceHistory.cost))
            .group_by(func.strftime('%Y-%m', MaintenanceHistory.created_at))
            .order_by("month")
        )
        results = session.exec(query).all()
        return [{"month": r[0], "cost": r[1]} for r in results]

    @staticmethod
    def get_preferences(session: Session):
        # module 및 option 대여 횟수는 UsageHistory를 통해 조회
        module_item_type = item_type.get_by_name(session, "module")
        option_item_type = item_type.get_by_name(session, "option")
        module_query = select(func.count()).select_from(UsageHistory).where(
            UsageHistory.item_type_id == module_item_type.item_type_id
        )
        option_query = select(func.count()).select_from(UsageHistory).where(
            UsageHistory.item_type_id == option_item_type.item_type_id
        )
        module_count = session.exec(module_query).one()
        option_count = session.exec(option_query).one()
        return {
            "moduleRentalCount": module_count,
            "optionRentalCount": option_count
        }

    @staticmethod
    def get_overall_dashboard_data(session: Session):
        top_cards = {
            "todayRentedVehicles": DashboardService.get_today_rented_vehicles_count(session),
            "currentlyRentingVehicles": DashboardService.get_currently_renting_vehicles_count(session),
            "todayExpectedReturnVehicles": DashboardService.get_today_expected_return_vehicles_count(session)
        }
        state_charts = {
            "vehicleStates": DashboardService.get_vehicle_state_chart(session),
            "moduleStates": DashboardService.get_module_state_chart(session),
            "optionStates": DashboardService.get_option_state_chart(session)
        }
        sales_statistics = {
            "rentalCountsByDate": DashboardService.get_rental_counts_by_date(session),
            "maintenanceCostByMonth": DashboardService.get_maintenance_cost_by_month(session)
        }
        preferences = DashboardService.get_preferences(session)
        return {
            "topCards": top_cards,
            "stateCharts": state_charts,
            "salesStatistics": sales_statistics,
            "preferences": preferences
        } 