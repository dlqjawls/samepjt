from typing import Optional
from collections import Counter
from app.schemas.user.option_types import OptionTypesResponse, OptionTypesData, OptionType
from app.dummy_data import dummy_options, dummy_option_types
from app.services.pagination import paginate


class OptionTypeService:
    """옵션 타입 목록 조회 서비스 클래스"""

    @staticmethod
    def get_option_types(page: int = 1, page_size: int = 10, option_type_id: Optional[int] = None) -> OptionTypesResponse:
        """ 옵션 타입별 목록을 조회합니다 """

        # 옵션 타입별 개수 집계
        option_counts = Counter([opt["optionType"] for opt in dummy_options])

        # 옵션 타입 목록 생성
        option_types = [
            OptionType(
                optionTypeId=opt_type["optionTypeId"],
                optionTypeName=opt_type["optionTypeName"],
                optionTypeSize=opt_type["optionTypeSize"],
                optionTypeCost=opt_type["optionTypeCost"],
                stockQuantity=option_counts.get(opt_type["optionTypeId"], 0),  # 해당 옵션 타입의 총 개수
                imgUrls=[opt_type["optionTypeImages"]],
                description=opt_type["description"]
            )
            for opt_type in dummy_option_types
        ]

        # 옵션 타입 ID로 필터링 (option_type_id 제공 시)
        if option_type_id is not None:
            option_types = [opt for opt in option_types if opt.optionTypeId == option_type_id]

        # 페이지네이션 적용
        paginated_result = paginate(option_types, page, page_size)

        # 응답 반환 
        return OptionTypesResponse(
            resultCode="SUCCESS",
            message="Option types retrieved successfully",
            data=OptionTypesData(
                optionTypes=paginated_result.items,  
                pagination=paginated_result.pagination
            )
        )
