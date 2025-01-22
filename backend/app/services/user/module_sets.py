from app.schemas.user.module_sets import ModuleSetsResponse, ModuleSetData, ModuleSet, SuppliedOption
from app.dummy_data import dummy_module_sets, dummy_module_set_options
from app.services.pagination import paginate

class ModuleSetService:
    """ 모듈 세트 목록 조회 서비스 클래스 """

    @staticmethod
    def get_module_sets(page: int = 1, page_size: int = 10) -> ModuleSetsResponse:
        """ 모듈 세트 목록을 조회합니다 """

        # 페이지네이션
        paginated_result = paginate(dummy_module_sets, page, page_size)

        # 모듈 세트 목록 생성
        module_sets = []
        for module_set in paginated_result.items:
            supplied_options = [
                SuppliedOption(
                    optionId=opt["optionId"],
                    optionName=f"Option {opt['optionId']}",
                    quantity=opt["quantity"]
                )
                for opt in dummy_module_set_options
                if opt["moduleSetId"] == module_set["moduleSetId"]
            ]

            # 모듈 세트 객체 생성
            module_sets.append(
                ModuleSet(
                    moduleSetId=module_set["moduleSetId"],
                    moduleSetName=module_set["moduleSetName"],
                    description=module_set["description"],
                    totalCost=module_set["totalCost"],
                    imgsUrls=module_set["imgsUrls"],
                    suppliedOptions=supplied_options
                )
            )

        # 응답 반환
        return ModuleSetsResponse(
            resultCode="SUCCESS",
            message="Module sets retrieved successfully",
            data=ModuleSetData(moduleSets=module_sets, pagination=paginated_result.pagination)
        )
