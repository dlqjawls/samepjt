from fastapi import HTTPException
from sqlmodel import Session
from app.crud.option_type import get_all_option_types, get_option_type_by_id, get_option_counts_by_type
from app.api.schemas.user.option_types import OptionTypesResponse, OptionTypesData, OptionType
from app.services.pagination import paginate
from app.models.option import Option as OptionModel
from typing import Optional

class OptionTypeService:

    @staticmethod
    def get_option_types(
        session: Session, 
        page: int = 1, 
        page_size: int = 10, 
        option_type_id: Optional[int] = None
    ) -> OptionTypesResponse:

        # 옵션 타입별 개수 집계
        option_counts = get_option_counts_by_type(session)

        # 옵션 타입 조회
        if option_type_id:
            option_types = [get_option_type_by_id(session, option_type_id)]
        else:
            option_types = get_all_option_types(session)

        if not option_types:  # 데이터가 없을 경우 빈 리스트 반환
            return OptionTypesResponse(
                resultCode="SUCCESS",
                message="No option types found",
                data=OptionTypesData(optionTypes=[], pagination={})
            )

        # 페이지네이션 적용
        paginated_result = paginate(option_types, page, page_size)

        # 옵션 타입 목록 생성
        option_types_data = [
            OptionType(
                optionTypeId=opt_type.optionTypeId,
                optionTypeName=opt_type.optionTypeName,
                optionTypeSize=opt_type.optionTypeSize,
                optionTypeCost=opt_type.optionTypeCost,
                stockQuantity=option_counts.get(opt_type.optionTypeId, 0),  # 해당 옵션 타입의 총 개수
                description=opt_type.description,
                imgUrls=[opt_type.optionTypeImages],
                optionTypeFeatures=opt_type.optionTypeFeatures
            )
            for opt_type in paginated_result.items if opt_type is not None  # None 값을 체크하여 무시
        ]


        return OptionTypesResponse(
            resultCode="SUCCESS",
            message="Option types retrieved successfully",
            data=OptionTypesData(optionTypes=option_types_data, pagination=paginated_result.pagination)
        )
