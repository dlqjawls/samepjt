from sqlalchemy import func
from sqlmodel import Session, select
from typing import List
from app.models.option import Option
from sqlalchemy.exc import SQLAlchemyError
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError

class OptionCRUD(CRUDBase[Option]):
    def __init__(self):
        super().__init__(Option, "option_id")
        
    def get_options_by_type(
        self,
        session: Session,
        option_type_id: int
    ) -> List[Option]:
        """특정 옵션 타입의 모든 옵션 조회"""
        try:
            # 유효성 검사
            if option_type_id <= 0:
                raise ValidationError(
                    message="Invalid option type ID",
                    detail={
                        "option_type_id": option_type_id,
                        "error": "Option type ID must be positive"
                    }
                )

            # 옵션 조회
            query = (
                select(self.model)
                .where(
                    self.model.option_type_id == option_type_id,
                    self.model.deleted_at == None  # soft delete
                )
            )
            
            results = list(session.exec(query).all())

            # 결과 검증
            if not results:
                raise NotFoundError(
                    message="No options found for the given type",
                    detail={
                        "option_type_id": option_type_id
                    }
                )

            return results

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch options",
                detail={
                    "error": str(e),
                    "option_type_id": option_type_id
                }
            )
            
    def get_available_options_by_type(
        self,
        session: Session,
        option_type_id: int,
        required_quantity: int,
        status_id: int = 2  # INACTIVE(대기 중) 상태
    ) -> List[Option]:
        try:
            # 1. 입력값 검증
            if option_type_id <= 0:
                raise ValidationError(
                    message="Invalid option type ID",
                    detail={
                        "option_type_id": option_type_id,
                        "error": "Option type ID must be positive"
                    }
                )

            if required_quantity <= 0:
                raise ValidationError(
                    message="Invalid quantity",
                    detail={
                        "required_quantity": required_quantity,
                        "error": "Quantity must be positive"
                    }
                )

            # 2. 사용 가능한 옵션 조회
            query = (
                select(self.model)
                .where(
                    self.model.option_type_id == option_type_id,
                    self.model.status_id == status_id,
                    self.model.deleted_at == None  # soft delete
                )
                .limit(required_quantity)
            )

            available_options = list(session.exec(query).all())

            # 3. 수량 검증
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
                detail={
                    "error": str(e),
                    "option_type_id": option_type_id,
                    "required_quantity": required_quantity
                }
            )

    def get_option_status_name(self, status_id: int) -> str:
        """
        주어진 옵션(status) ID에 해당하는 이름을 반환합니다.
        """
        from app.crud.lut import get_item_status_mapping
        mapping = get_item_status_mapping()
        return mapping.get(status_id, "Unknown")

option_crud = OptionCRUD()