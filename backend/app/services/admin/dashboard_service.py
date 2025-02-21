from datetime import date, datetime, time, timedelta
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
from app.utils.lut_constants import ItemType, RentStatus
from app.db.crud.option_type import option_type_crud

class DashboardService:
    # 차량 관련 데이터
    @staticmethod
    def get_today_rented_vehicles_count(session: Session) -> int:
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        query = select(RentHistory).where(RentHistory.created_at >= start, RentHistory.created_at <= end, RentHistory.rent_status_id == RentStatus.IN_PROGRESS.ID)
        paginated = rent_history_crud.paginate(session, 1, 1000, query)
        return paginated["pagination"]["totalItems"]

    @staticmethod
    def get_currently_renting_vehicles_count(session: Session) -> int:
        query = select(RentHistory).where(RentHistory.rent_status_id == RentStatus.IN_PROGRESS.ID)
        results = session.exec(query).all()
        return len(results)

    @staticmethod
    def get_today_expected_return_vehicles_count(session: Session) -> int:
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        query = select(RentHistory).where(RentHistory.rent_end_date >= start, RentHistory.rent_end_date <= end)
        results = session.exec(query).all()
        return len(results)

    @staticmethod
    def get_today_completed_returns_count(session: Session) -> int:
        """ 오늘 날짜에 반납 완료된 차량 건수를 조회합니다. """
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        query = (
            select(RentHistory)
            .where(
                RentHistory.updated_at >= start,
                RentHistory.updated_at <= end,
                RentHistory.rent_status_id == RentStatus.COMPLETED.ID
            )
        )
        results = session.exec(query).all()
        return len(results)

    @staticmethod
    def get_state_chart(query_model, count_field, session: Session):
        total = session.exec(select(func.count()).select_from(query_model)).one()
        group_query = (
            select(getattr(query_model, "item_status_id"), func.count(count_field))
            .group_by(getattr(query_model, "item_status_id"))
        )
        results = session.exec(group_query).all()
        state_chart = []
        for status_id, cnt in results:
            status_obj = item_status.get_by_id(session, status_id)
            ratio = (cnt / total * 100) if total > 0 else 0
            # 소수점 첫째자리에서 올림 (예: 50.1, 50.2 ... 50.9를 50.1로 올림)
            ratio = math.ceil(ratio * 10) / 10  
            state_chart.append({
                "state": status_obj.item_status_name,
                "count": cnt,
                "ratio": ratio
            })
        return state_chart

    @staticmethod
    def get_vehicle_state_chart(session: Session):
        return DashboardService.get_state_chart(Vehicle, Vehicle.vehicle_id, session)

    @staticmethod
    def get_module_state_chart(session: Session):
        return DashboardService.get_state_chart(Module, Module.module_id, session)

    @staticmethod
    def get_option_state_chart(session: Session):
        return DashboardService.get_state_chart(Option, Option.option_id, session)

    # 판매 통계 관련 데이터
    @staticmethod
    def get_rental_counts_by_date(session: Session) -> list:
        """월별 대여 건수를 조회합니다."""
        query = (
            select(
                func.strftime("%Y-%m", RentHistory.rent_start_date).label("year_month"),
                func.count().label("count")
            )
            .group_by("year_month")
        )
        results = session.exec(query).all()  
        monthly_counts = [
            {"month": f"{int(year_month.split('-')[1])}월", "count": count}
            for year_month, count in results
        ]
        return monthly_counts

    @staticmethod
    def get_maintenance_cost_by_month(session: Session) -> list:
        """월별 정비 비용을 조회합니다."""
        query = (
            select(
                func.strftime("%Y-%m", MaintenanceHistory.scheduled_at).label("year_month"),
                func.sum(MaintenanceHistory.cost).label("cost")
            )
            .group_by("year_month")
        )
        results = session.exec(query).all()  # results: 리스트 형태 [(year_month, cost), ...]
        monthly_costs = [{"month": year_month, "cost": cost} for year_month, cost in results]
        return monthly_costs

    @staticmethod
    def get_popular_option_types(session: Session) -> list:
        """
        최근 3개월 내 대여된 옵션 기록을 기반으로 
        옵션 타입별 사용 건수를 집계하고 상위 5개 항목을 반환합니다.
        """
        three_months_ago = datetime.now() - timedelta(days=90)
        stmt = (
            select(Option.option_type_id, func.count(UsageHistory.usage_id).label("cnt"))
            .join(Option, Option.option_id == UsageHistory.item_id)
            .where(
                UsageHistory.item_type_id == ItemType.OPTION.ID,
                UsageHistory.created_at >= three_months_ago
            )
            .group_by(Option.option_type_id)
            .order_by(func.count(UsageHistory.usage_id).desc())
            .limit(5)
        )
        results = session.exec(stmt).all()
        popular = []
        for opt_type_id, count in results:
            # 조회된 옵션 타입 이름을 가져옴
            name = option_type_crud.get_option_name_by_id(session, opt_type_id)
            popular.append({
                "option_type_id": opt_type_id,
                "option_type_name": name,
                "count": count
            })
        return popular
