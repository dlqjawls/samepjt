from app.api.schemas.user.module_sets import ModuleSetsResponse, ModuleSetData, ModuleSet, moduleSetOptionType
from app.core.database import get_session
from app.models.module_set import ModuleSet as ModuleSetModel
from app.models.module_set_option_type import ModuleSetOptionType as ModuleSetOptionTypeModel
from app.models.option_type import OptionType as OptionTypeModel
from app.services.pagination import paginate
from sqlmodel import select

class ModuleSetService:
    """ 모듈 세트 목록 조회 서비스 클래스 """

    @staticmethod
    def get_module_sets(page: int = 1, page_size: int = 10) -> ModuleSetsResponse:
        """ 모듈 세트 목록을 조회합니다 """

        with get_session() as session:
            # 모듈 세트 조회
            statement = select(ModuleSetModel)
            module_sets = session.exec(statement).all()

            # 페이지네이션 적용
            paginated_result = paginate(module_sets, page, page_size)

            # 모듈 세트 목록 생성
            module_sets_data = []
            for module_set in paginated_result.items:
                module_set_option_types = []

                # 해당 모듈 세트에 속한 옵션 타입을 가져옴
                statement = select(ModuleSetOptionTypeModel).where(ModuleSetOptionTypeModel.moduleSetId == module_set.moduleSetId)
                module_set_option_types_data = session.exec(statement).all()

                for opt in module_set_option_types_data:
                    # 옵션 타입 ID로 옵션 타입 정보 가져오기
                    statement = select(OptionTypeModel).where(OptionTypeModel.optionTypeId == opt.optionTypeId)
                    option_type = session.exec(statement).first()

                    if option_type:
                        module_set_option_types.append(
                            moduleSetOptionType(
                                optionTypeId=option_type.optionTypeId,
                                optionTypeName=option_type.optionTypeName,
                                quantity=opt.quantity
                            )
                        )

                module_sets_data.append(
                    ModuleSet(
                        moduleSetId=module_set.moduleSetId,
                        moduleSetName=module_set.moduleSetName,
                        description=module_set.description,
                        basePrice=module_set.basePrice,
                        imgsUrls=module_set.moduleSetImages.split(','),  # 문자열을 리스트로 변환
                        moduleSetOptionTypes=module_set_option_types
                    )
                )

            return ModuleSetsResponse(
                resultCode="SUCCESS",
                message="Module sets retrieved successfully",
                data=ModuleSetData(moduleSets=module_sets_data, pagination=paginated_result.pagination)
            )