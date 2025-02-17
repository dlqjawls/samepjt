from sqlmodel import Session, select
from app.db.models.rent_history import RentHistory
from app.utils.lut_constants import RentStatus
from app.api.schemas.user.me_schema import MeRentInfo, MeRentInfoResponse, MeRentHistoryResponse
from app.utils.handle_transaction import handle_transaction
from app.db.crud.rent_history import rent_history_crud

class MeRentInfoService:
  
    @staticmethod
    @handle_transaction
    def get_current_rent_info(session: Session, user_pk: int) -> MeRentInfoResponse:
        """사용자 PK를 기반으로 진행 중인 렌트 정보 조회"""
        rent_history = rent_history_crud.get_rents_by_user(session, user_pk, RentStatus.IN_PROGRESS.ID)
        
        response = MeRentInfo(
            rent_id=rent_history[0].rent_id if rent_history else None,
            rentStartDate=rent_history[0].rent_start_date if rent_history else None,
            rentEndDate=rent_history[0].rent_end_date if rent_history else None,
            cost=rent_history[0].cost if rent_history else None
        )
        return MeRentInfoResponse.success(
            message="Current rent info retrieved successfully",
            data=response
        )
        
    @staticmethod
    @handle_transaction
    def get_rent_history(session: Session, user_pk: int) -> MeRentHistoryResponse:
        """사용자 PK를 기반으로 렌트 이력 조회"""
        rent_histories = rent_history_crud.get_rents_by_user(session, user_pk)
        response = [
            MeRentInfo(
                rent_id=rent_history.rent_id,
                rentStartDate=rent_history.rent_start_date, 
                rentEndDate=rent_history.rent_end_date,
                cost=rent_history.cost
            )
            for rent_history in rent_histories
        ]
        return MeRentHistoryResponse.success(
            message="Rent history retrieved successfully",
            data=response
        ) 
        
