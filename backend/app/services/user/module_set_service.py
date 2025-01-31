from sqlmodel import Session
from typing import List, Tuple
from app.models.module_set import ModuleSet
from app.models.option_type import OptionType
from app.models.module_set_option_types import ModuleSetOptionTypes
from app.crud.module_set import module_set_crud
from app.crud.module_set_option_type import module_set_option_type_crud
from app.api.schemas.user import module_set_schema
from app.utils.handle_transaction import handle_transaction
from app.utils.exceptions import (
    DatabaseError, 
)

class ModuleSetServiceUtils:
    """ 🎯 ModuleSetService 관련 공통 로직을 관리하는 유틸리티 클래스 """

    @staticmethod
    def get_option_types(session: Session, module_set_id: int) -> List[module_set_schema.ModuleSetOptionType]:
        """ ✅ 특정 모듈 세트에 속한 옵션 타입 조회 및 변환 """
        option_types: List[Tuple[OptionType, ModuleSetOptionTypes]] = module_set_option_type_crud.get_option_types_by_module_set(
            session, module_set_id
        )

        module_set_option_types = []
        for option_type, module_set_option in option_types:
            if option_type.option_type_id is None or option_type.option_type_name is None:
                raise DatabaseError(
                    message="Data inconsistency in option types",
                    detail={
                        "module_set_id": module_set_id,
                        "option_type": option_type.dict() if option_type else None
                    }
                )


            module_set_option_types.append(
                module_set_schema.ModuleSetOptionType(
                    optionTypeId=option_type.option_type_id,
                    optionTypeName=option_type.option_type_name,
                    quantity=module_set_option.option_quantity or 0  # ✅ `None`일 경우 기본값 `0`
                )
            )
        return module_set_option_types


class ModuleSetService:
    """ 🎯 사용자용 모듈 세트 조회 서비스 클래스 """

    @staticmethod
    @handle_transaction
    def get_all_module_sets(session: Session, page: int = 1, page_size: int = 10) -> module_set_schema.ModuleSetsResponse:
        """ ✅ 모든 모듈 세트 목록을 조회하고, 옵션 타입 정보를 함께 반환합니다. """

        # ✅ 페이지네이션 적용하여 모듈 세트 조회
        paginated_result = module_set_crud.get_all(session, page, page_size)
        module_sets: List[ModuleSet] = paginated_result["items"]

        module_sets_data: List[module_set_schema.ModuleSet] = []

        for module_set in module_sets:
            
            if module_set.module_set_id is None:
                raise DatabaseError(
                    message="ModuleSet ID cannot be None",
                    detail={"module_set": module_set.dict(exclude={"created_at", "updated_at", "deleted_at"})}
                )

            module_set_option_types = ModuleSetServiceUtils.get_option_types(session, module_set.module_set_id)

            # datetime 필드를 제외하고 필요한 필드만 응답 모델로 변환
            module_sets_data.append(
                module_set_schema.ModuleSet(
                    moduleSetId=module_set.module_set_id,
                    moduleSetName=module_set.module_set_name or "No name available",
                    description=module_set.description or "No description available",
                    basePrice=module_set.base_price or 0.0,
                    imgUrls=module_set.module_set_images.split(',') if module_set.module_set_images else [],
                    moduleSetOptionTypes=module_set_option_types
                )
            )
            
        return module_set_schema.ModuleSetsResponse.success(
            message="Module sets retrieved successfully",
            data=module_set_schema.ModuleSetData(
                moduleSets=module_sets_data, 
                pagination=paginated_result["pagination"]
            )
        )