from sqlmodel import Session, select
from app.db.models.rent_history import RentHistory
from app.utils.lut_constants import RentStatus
from app.utils.exceptions import DatabaseError, NotFoundError
from app.api.schemas.user.me_schema import MeRentInfo
from app.utils.handle_transaction import handle_transaction

class MeRentInfoService:
    @staticmethod
    @handle_transaction
    def get_current_rent_info(session: Session, user_pk: int) -> MeRentInfo:
        """
        사용자 PK를 기반으로 진행 중인 렌트 정보를 조회하는 서비스 로직입니다.
        
        Args:
            session (Session): 데이터베이스 세션
            user_pk (int): 사용자의 고유 식별자
        
        Returns:
            MeRentInfo: 진행 중인 렌트 정보 (rent_id 포함)
        
        Raises:
            NotFoundError: 진행 중인 렌트 정보가 없을 경우 발생
        """
        query = select(RentHistory).where(
            RentHistory.user_pk == user_pk,
            RentHistory.status_id == RentStatus.IN_PROGRESS
        )
        rent_history = session.exec(query).first()
        if not rent_history:
            raise NotFoundError(
                message="진행 중인 렌트 정보가 존재하지 않습니다.",
                detail={"user_pk": user_pk}
            )
        if rent_history.rent_id is None:
            raise DatabaseError(
                message="렌트 정보가 존재하지 않습니다.",
                detail={"rent_id": rent_history.rent_id}
            )
            
        return MeRentInfo(rent_id=rent_history.rent_id) 