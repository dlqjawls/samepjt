from fastapi import HTTPException
from app.models.module_set import ModuleSetListResponse, ModuleSetData, ModuleSet, SuppliedOption, Pagination
from app.dummy_data import dummy_module_sets, dummy_module_set_options


class ModuleSetService:
    """🛠️ 모듈 세트 목록을 조회하는 서비스 클래스"""

    @staticmethod
    def get_module_sets(page: int = 1, page_size: int = 10) -> ModuleSetListResponse:
        """모듈 세트 목록을 조회하고 페이지네이션을 적용"""

        total_items = len(dummy_module_sets)
        total_pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)

        if page > total_pages and total_pages != 0:
            raise HTTPException(
                status_code=404,
                detail={
                    "resultCode": "FAILURE",
                    "message": "No matching module sets found",
                    "data": None
                }
            )

        module_sets = dummy_module_sets[(page - 1) * page_size : page * page_size]

        module_set_list = []
        for module_set in module_sets:
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

        pagination = Pagination(
            currentPage=page,
            totalPages=total_pages,
            totalItems=total_items,
            pageSize=page_size
        )

        return ModuleSetListResponse(
            resultCode="SUCCESS",
            message="Module sets retrieved successfully",
            data=ModuleSetData(moduleSets=module_set_list, pagination=pagination) 
        )
