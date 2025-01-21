from fastapi import HTTPException
from app.schemas.user.option_list import OptionListResponse, OptionListData, Option
from app.dummy_data import dummy_options
from app.services.pagination import paginate

class OptionService:
    """🛠️ 옵션 목록을 조회하는 서비스 클래스"""

    @staticmethod
    def get_options(page: int = 1, page_size: int = 10, option_id: int = None) -> OptionListResponse:
        """옵션 목록을 조회하고 페이지네이션을 적용"""

        # ✅ ID 기반 검색 필터 적용
        filtered_options = dummy_options
        if option_id:
            filtered_options = [opt for opt in dummy_options if opt["optionId"] == option_id]

        # ✅ 공통 페이지네이션 로직 적용
        paginated_result = paginate(filtered_options, page, page_size)

        # ✅ 옵션이 없을 경우 404 예외 발생
        if not paginated_result.items:
            raise HTTPException(
                status_code=404,
                detail={
                    "resultCode": "FAILURE",
                    "message": "No matching options found",
                    "data": None
                }
            )

        option_list = [
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

        return OptionListResponse(
            resultCode="SUCCESS",
            message="Options retrieved successfully",
            data=OptionListData(
                options=option_list,
                pagination=paginated_result.pagination
            )
        )
