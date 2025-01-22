from app.schemas.user.module_sets import ModuleSetsResponse, ModuleSetData, ModuleSet, moduleSetOptionType
from app.dummy_data import dummy_module_sets, dummy_module_set_option_types, dummy_option_types
from app.services.pagination import paginate

class ModuleSetService:
    """ 모듈 세트 목록 조회 서비스 클래스 """

    @staticmethod
    def get_module_sets(page: int = 1, page_size: int = 10) -> ModuleSetsResponse:
        """ 모듈 세트 목록을 조회합니다 """

        # 페이지네이션 적용
        paginated_result = paginate(dummy_module_sets, page, page_size)

        # 모듈 세트 목록 생성
        module_sets = []
        for module_set in paginated_result.items:
            module_set_option_types = []
            
            # 해당 모듈 세트에 속한 옵션 타입을 가져옴
            for opt in dummy_module_set_option_types:
                if opt["moduleSetId"] == module_set["moduleSetId"]:
                    # 옵션 타입 ID로 옵션 타입 정보 가져오기
                    option_type = next(
                        (otype for otype in dummy_option_types if otype["optionTypeId"] == opt["optionTypeId"]),
                        None
                    )
                    
                    if option_type:
                        module_set_option_types.append(
                            moduleSetOptionType(
                                optionTypeId=option_type["optionTypeId"],
                                optionTypeName=option_type["optionTypeName"],
                                quantity=opt["quantity"]
                            )
                        )

            # 모듈 세트 객체 생성
            module_sets.append(
                ModuleSet(
                    moduleSetId=module_set["moduleSetId"],
                    moduleSetName=module_set["moduleSetName"],
                    description=module_set["description"],
                    basePrice=module_set["basePrice"], 
                    imgsUrls=[module_set["moduleSetImages"]],
                    moduleSetOptionTypes=module_set_option_types
                )
            )

        # 응답 반환
        return ModuleSetsResponse(
            resultCode="SUCCESS",
            message="Module sets retrieved successfully",
            data=ModuleSetData(moduleSets=module_sets, pagination=paginated_result.pagination)
        )
