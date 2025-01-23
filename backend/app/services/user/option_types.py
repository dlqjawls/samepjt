from typing import Optional
from app.api.schemas.user.option_types import OptionTypesResponse, OptionTypesData, OptionType
from app.core.database import get_session
from app.models.option import Option as OptionModel
from app.models.option_type import OptionType as OptionTypeModel
from app.services.pagination import paginate
from sqlmodel import select, func

class OptionTypeService:
    """옵션 타입 목록 조회 서비스 클래스"""

    @staticmethod
    def get_option_types(page: int = 1, page_size: int = 10, option_type_id: Optional[int] = None) -> OptionTypesResponse:
        """ 옵션 타입별 목록을 조회합니다 """

        with get_session() as session:
            # 옵션 타입별 개수 집계
            statement = select(OptionModel.optionType, func.count(OptionModel.optionType)).group_by(OptionModel.optionType)
            option_counts = dict(session.exec(statement).all())

            # 옵션 타입 조회
            statement = select(OptionTypeModel)
            if option_type_id:
                statement = statement.where(OptionTypeModel.optionTypeId == option_type_id)
            option_types = session.exec(statement).all()

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
                    optionTypeImages=opt_type.optionTypeImages,
                    optionTypeFeatures=opt_type.optionTypeFeatures
                )
                for opt_type in paginated_result.items
            ]

            return OptionTypesResponse(
                resultCode="SUCCESS",
                message="Option types retrieved successfully",
                data=OptionTypesData(optionTypes=option_types_data, pagination=paginated_result.pagination)
            )