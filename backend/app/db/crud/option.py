from sqlalchemy import func
from sqlmodel import Session, select
from typing import List
from app.db.models.option import Option
from sqlalchemy.exc import SQLAlchemyError
from app.db.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError
from app.utils.lut_constants import ItemStatus

class OptionCRUD(CRUDBase[Option]):
    def __init__(self):
        super().__init__(Option)
        
    def get_by_id(self, session: Session, option_id: int) -> Option:
        """주어진 ID에 해당하는 옵션을 조회합니다.

        Args:
            session (Session): DB 세션
            option_id (int): 옵션 ID

        Returns:
            Option: 조회된 옵션 객체

        Raises:
            ValidationError: 옵션 ID가 유효하지 않은 경우
            NotFoundError: 해당 ID에 해당하는 옵션이 없는 경우
            DatabaseError: 옵션 조회 중 DB 오류 발생 시
        """
        if option_id <= 0:
            raise ValidationError(
                message="Invalid option ID",
                detail={"option_id": option_id, "error": "Option ID must be positive"}
            )

        option = self.get_by_field(session, self.model.option_id, "option_id")
        if not option:
            raise NotFoundError(
                message="Option not found",
                detail={"option_id": option_id}
            ) 
        return option

    def get_options_by_type(
        self,
        session: Session,
        option_type_id: int
    ) -> List[Option]:
        """특정 옵션 타입의 모든 옵션을 조회합니다.

        Args:
            session (Session): DB 세션
            option_type_id (int): 옵션 타입 ID

        Returns:
            List[Option]: 조회된 옵션 리스트

        Raises:
            ValidationError: 옵션 타입 ID가 유효하지 않은 경우
            NotFoundError: 해당 옵션 타입에 해당하는 옵션이 없는 경우
            DatabaseError: 옵션 조회 중 DB 오류 발생 시
        """
        if option_type_id <= 0:
            raise ValidationError(
                message="Invalid option type ID",
                detail={"option_type_id": option_type_id, "error": "Option type ID must be positive"}
            )

        try:
            query = select(self.model).where(
                self.model.option_type_id == option_type_id,
                self.model.deleted_at == None  # soft delete check
            )
            results = list(session.exec(query).all())

            if not results:
                raise NotFoundError(
                    message="No options found for the given type",
                    detail={"option_type_id": option_type_id}
                )
            return results
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch options",
                detail={"error": str(e), "option_type_id": option_type_id}
            )
            
    def get_available_options_by_type(
        self,
        session: Session,
        option_type_id: int,
        required_quantity: int,
        item_status_id: int = ItemStatus.INACTIVE.ID
    ) -> List[Option]:
        """특정 옵션 타입에서 사용 가능한 옵션을 조회합니다.


        Args:
            session (Session): DB 세션
            option_type_id (int): 옵션 타입 ID
              required_quantity (int): 필요한 옵션 수량
            item_status_id (int, optional): 옵션 상태 ID. Defaults to 2.


        Returns:
            List[Option]: 사용 가능한 옵션 리스트

        Raises:
            ValidationError: 입력값이 유효하지 않은 경우
            NotFoundError: 요구된 수량만큼의 옵션을 찾지 못한 경우
            DatabaseError: 옵션 조회 중 DB 오류 발생 시
        """
        if option_type_id <= 0:
            raise ValidationError(
                message="Invalid option type ID",
                detail={"option_type_id": option_type_id, "error": "Option type ID must be positive"}
            )

        if required_quantity <= 0:
            raise ValidationError(
                message="Invalid quantity",
                detail={"required_quantity": required_quantity, "error": "Quantity must be positive"}
            )

        try:
            query = select(self.model).where(
                self.model.option_type_id == option_type_id,
                self.model.item_status_id == item_status_id,
                self.model.deleted_at == None  # soft delete check
            ).limit(required_quantity)


            available_options = list(session.exec(query).all())

            if len(available_options) < required_quantity:
                raise NotFoundError(
                    message="Not enough available options",
                    detail={
                        "option_type_id": option_type_id,
                        "required": required_quantity,
                        "available": len(available_options)
                    }
                )
            return available_options
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch available options",
                detail={"error": str(e), "option_type_id": option_type_id, "required_quantity": required_quantity}
            )

option_crud = OptionCRUD()