from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError
from app.utils.exceptions import DatabaseError
from app.db.models.option_type import OptionType
from app.db.models.option import Option
from app.db.crud.base import CRUDBase

class OptionTypeCRUD(CRUDBase[OptionType]):
    def __init__(self):
        super().__init__(OptionType)

    def get_option_counts_by_type(self, session: Session) -> dict:
        """옵션 타입 별 옵션 개수를 조회합니다.

        Args:
            session (Session): DB 세션

        Returns:
            dict: {option_type_id: count, ...}

        Raises:
            DatabaseError: DB 조회 중 오류 발생 시
        """
        try:
            statement = select(Option.option_type_id, func.count()).group_by(Option.option_type_id)
            counts = dict(session.exec(statement).all())
            return counts
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch option type counts",
                detail={"error": str(e)}
            )
            
            
    def get_option_name_by_id(self, session: Session, option_type_id: int) -> str:
        """옵션 타입 ID에 해당하는 옵션 이름을 조회합니다.

        Args:
            session (Session): DB 세션
            option_type_id (int): 옵션 타입 ID

        Returns:
            str: 옵션 이름

        Raises:
            DatabaseError: DB 조회 중 오류 발생 시
        """ 
        try:
            option = session.exec(select(OptionType).where(OptionType.option_type_id == option_type_id)).first()
            return option.option_type_name if option else "Unknown"
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch option name",
                detail={"error": str(e)}
            )

option_types_crud = OptionTypeCRUD()
