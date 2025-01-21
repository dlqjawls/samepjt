from typing import Optional
from app.schemas.user.options import OptionsResponse, OptionsData, Option
from app.dummy_data import dummy_options
from app.services.pagination import paginate

class OptionService:
    """옵션 목록 조회 서비스 클래스"""

    @staticmethod
    def get_options(page: int = 1, page_size: int = 10, option_id: Optional[int] = None) -> OptionsResponse:
        """ 옵션 목록을 조회합니다 """

        # 옵션 목록 필터링
        filtered_options = dummy_options
        if option_id:
            filtered_options = [opt for opt in dummy_options if opt["optionId"] == option_id]

        # 페이지네이션 적용
        paginated_result = paginate(filtered_options, page, page_size)

        # 옵션 목록 생성
        options = [
            Option(
                optionId=option["optionId"],
                optionName=option["optionName"],
                optionSize=option["optionSize"],
                optionCost=option["optionCost"],
                optionType=option["optionType"],
                stockQuantity=option["stockQuantity"],
                imgUrls=option["imgUrls"],
                description=option["description"]
            )
            for option in paginated_result.items
        ]

        # 응답 반환 
        return OptionsResponse(
            resultCode="SUCCESS",
            message="Options retrieved successfully",
            data=OptionsData(
                options=options,  
                pagination=paginated_result.pagination
            )
        )
