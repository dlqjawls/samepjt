from fastapi import HTTPException
from app.schemas.user.module_set import ModuleSetListResponse, ModuleSetData, ModuleSet, SuppliedOption
from app.dummy_data import dummy_module_sets, dummy_module_set_options
from app.services.pagination import paginate

class ModuleSetService:
    """🛠️ 모듈 세트 목록을 조회하는 서비스 클래스"""

    @staticmethod
    def get_module_sets(page: int = 1, page_size: int = 10) -> ModuleSetListResponse:
        """모듈 세트 목록을 조회하고 페이지네이션을 적용"""

        # ✅ 공통 페이지네이션 로직 적용
        paginated_result = paginate(dummy_module_sets, page, page_size)

        # ✅ 모듈 세트가 없을 경우 404 예외 발생
        if not paginated_result.items:
            raise HTTPException(
                status_code=404,
                detail={
                    "resultCode": "FAILURE",
                    "message": "No matching module sets found",
                    "data": None
                }
            )

        module_set_list = []
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

            module_set_list.append(
                ModuleSet(
                    moduleSetId=module_set["moduleSetId"],
                    moduleSetName=module_set["moduleSetName"],
                    description=module_set["description"],
                    totalCost=module_set["totalCost"],
                    imgsUrls=module_set["imgsUrls"],
                    createdAt=module_set["createdAt"],
                    updatedAt=module_set["updatedAt"],
                    suppliedOptions=supplied_options
                )
            )

        return ModuleSetListResponse(
            resultCode="SUCCESS",
            message="Module sets retrieved successfully",
            data=ModuleSetData(moduleSets=module_set_list, pagination=paginated_result.pagination)
        )
