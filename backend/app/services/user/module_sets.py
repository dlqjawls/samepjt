from sqlmodel import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from app.crud.module_set import get_all_module_sets
from app.crud.option_type import get_option_types_by_module_set_id
from app.api.schemas.user.module_sets import ModuleSetsResponse, ModuleSetData, ModuleSet, moduleSetOptionType
from app.services.pagination import paginate
from fastapi import HTTPException

class ModuleSetService:
    """ 모듈 세트 목록 조회 서비스 클래스 """

    @staticmethod
    def get_module_sets(session: Session, page: int = 1, page_size: int = 10) -> ModuleSetsResponse:
        """ 모듈 세트 목록을 조회하고, 각 모듈 세트의 옵션 타입 정보를 함께 반환합니다. """

        try:
            # 모든 모듈 세트 조회 (CRUD 계층 함수 사용)
            module_sets = get_all_module_sets(session)

            # 페이지네이션 적용
            paginated_result = paginate(module_sets, page, page_size)

            module_sets_data = []
            for module_set in paginated_result.items:
                module_set_option_types = []

                # 해당 모듈 세트에 속한 옵션 타입 조회 (CRUD 사용)
                option_types = get_option_types_by_module_set_id(session, module_set.moduleSetId)

                for option_type, module_set_option in option_types:
                    module_set_option_types.append(
                        moduleSetOptionType(
                            optionTypeId=option_type.optionTypeId,
                            optionTypeName=option_type.optionTypeName,
                            quantity=module_set_option.quantity
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
        
        except NoResultFound:
            raise HTTPException(status_code=404, detail="No module sets found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

