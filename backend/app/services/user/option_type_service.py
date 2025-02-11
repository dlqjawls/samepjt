from sqlmodel import Session
from typing import List
from app.db.models.option_type import OptionType 
from app.db.crud.option_type import option_type_crud
from app.api.schemas.user import option_type_schema
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.handle_transaction import handle_transaction

class OptionTypeServiceUtils:

    @staticmethod
    def convert_to_schema(
        option_type: OptionType, 
        stock_quantity: int = 0
    ) -> option_type_schema.OptionType: 
        """ ✅ OptionType 모델을 Pydantic 스키마로 변환 """
        
        """옵션 타입 필수 필드 검증"""
        if not isinstance(option_type, OptionType):
            raise ValidationError(
                message="Invalid option type object",
                detail={
                    "error": "Expected OptionType instance",
                    "received": type(option_type).__name__
                }
            )

        if option_type.option_type_id is None:
            raise ValidationError(
                message="Required option type fields are missing",
                detail={
                    "option_type.option_type_id": {option_type.option_type_id},
                }
            )
            
        if option_type.option_type_name is None:
            raise ValidationError(
                message="Required option type fields are missing",
                detail={
                    "option_type.option_type_name": {option_type.option_type_name}
                }
            )

        # 옵션 ID 양수값 검증
        if option_type.option_type_id <= 0:
            raise ValidationError(
                message="Option type ID must be positive",
                detail={
                    "field": "option_type_id",
                    "value": option_type.option_type_id
                }
            )
        
        return option_type_schema.OptionType(
            optionTypeId=option_type.option_type_id,
            optionTypeName=option_type.option_type_name,
            optionTypeSize=option_type.option_type_size or "N/A",
            optionTypeCost=option_type.option_type_cost or 0.0,
            stockQuantity=stock_quantity,
            description=option_type.description or "",
            imgUrls=[option_type.option_type_images] if option_type.option_type_images else []
        )


class OptionTypeService:
    """ 🎯 옵션 타입 조회 서비스 """

    @staticmethod
    @handle_transaction
    def get_all_option_types(session: Session, page: int = 1, page_size: int = 10) -> option_type_schema.OptionTypesResponse:
        """ ✅ 옵션 타입 목록 조회 (페이지네이션 적용) """
        
        paginated_result = option_type_crud.paginate(session, page, page_size)
        option_types: List[OptionType] = paginated_result["items"]


        option_types_data = [
            OptionTypeServiceUtils.convert_to_schema(
                opt_type,
                option_type_crud.get_option_counts_by_type(session).get(opt_type.option_type_id, 0)
            )
            for opt_type in option_types
        ]

        return option_type_schema.OptionTypesResponse(
            resultCode="SUCCESS",
            message="Option types retrieved successfully",
            data=option_type_schema.OptionTypesData(
                optionTypes=option_types_data,
                pagination=paginated_result["pagination"]
            )
        )

    @staticmethod
    @handle_transaction
    def get_option_type_by_id(session: Session, option_type_id: int) -> option_type_schema.OptionTypesResponse:
        """ ✅ 특정 옵션 타입 조회 """
        if option_type_id <= 0:
            raise ValidationError(
                message="Option type ID must be positive",
                detail={"option_type_id": option_type_id}
            )
        
        option_type = option_type_crud.get_by_field(session, option_type_id, "option_type_id")
        if option_type is None:
            raise NotFoundError(
                message="Option type not found",    
                detail={"option_type_id": option_type_id}
            )
            
        option_type_data = OptionTypeServiceUtils.convert_to_schema(
            option_type,
            option_type_crud.get_option_counts_by_type(session).get(option_type.option_type_id, 0)
        )

        return option_type_schema.OptionTypesResponse(
            resultCode="SUCCESS",
            message="Option type retrieved successfully",
            data=option_type_schema.OptionTypesData(
                optionTypes=[option_type_data],
            )
        )
