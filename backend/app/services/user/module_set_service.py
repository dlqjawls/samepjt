from sqlmodel import Session
from typing import List, Tuple
from app.db.models.module_set import ModuleSet
from app.db.models.option_type import OptionType
from app.db.models.module_set_option_types import ModuleSetOptionTypes
from app.db.crud.module_set import module_set_crud
from app.db.crud.module_set_option_type import module_set_option_type_crud
from app.db.crud.option_type import option_type_crud
from app.db.crud.lut import module_type
from app.api.schemas.user import module_set_schema
from app.utils.handle_transaction import handle_transaction
from app.utils.exceptions import (
    DatabaseError, 
)



class ModuleSetService:
  
    @staticmethod
    def get_option_types(session: Session, module_set_id: int) -> List[module_set_schema.ModuleSetOptionType]:
        """ ✅ 특정 모듈 세트에 속한 옵션 타입 조회 및 변환 """
        option_types: List[ModuleSetOptionTypes] = module_set_option_type_crud.get_option_types_by_module_set(session, module_set_id)

        module_set_option_types = []
        for module_option in option_types:
            module_set_option_types.append(
                module_set_schema.ModuleSetOptionType(
                    optionTypeId=module_option.option_type_id,
                    optionTypeName=option_type_crud.get_option_name_by_id(session, module_option.option_type_id),
                    quantity=module_option.option_quantity or 1 # `None`일 경우 기본값 `1`
                )
            )
        return module_set_option_types

    @staticmethod
    @handle_transaction
    def get_all_module_sets(session: Session, page: int = 1, page_size: int = 10) -> module_set_schema.ModuleSetsResponse:

        """ ✅ 모든 모듈 세트 목록을 조회하고, 옵션 타입 정보를 함께 반환합니다. """

        # ✅ 페이지네이션 적용하여 모듈 세트 조회
        paginated_result = module_set_crud.paginate(session, page, page_size)
        module_sets: List[ModuleSet] = paginated_result["items"]

        module_sets_data: List[module_set_schema.ModuleSet] = []
        
        module_type_list = module_type.get_all(session)
        module_type_dict = {module_type.module_type_id: module_type for module_type in module_type_list}
        
        for module_set in module_sets:            
            if module_set.module_set_id is None:
                raise DatabaseError(
                    message="ModuleSet ID cannot be None",
                    detail={"module_set": module_set.dict(exclude={"created_at", "updated_at", "deleted_at"})}
                )

            module_type_info = module_type_dict.get(module_set.module_type_id)
            if module_type_info is None:
                raise DatabaseError(
                    message="ModuleType ID not found",
                    detail={"module_type_id": module_set.module_type_id}
                )

            module_set_option_types = ModuleSetService.get_option_types(session, module_set.module_set_id)

            base_price = module_set_crud.calculate_base_price(session, module_set.module_set_id)
            
            # datetime 필드를 제외하고 필요한 필드만 응답 모델로 변환
            module_sets_data.append(
                module_set_schema.ModuleSet(
                    moduleSetId=module_set.module_set_id,
                    moduleSetName=module_set.module_set_name,
                    description=module_set.description or "",
                    moduleTypeId=module_set.module_type_id,
                    moduleTypeName=module_type_info.module_type_name,
                    moduleTypeSize=module_type_info.module_type_size,
                    moduleTypeCost=int(module_type_info.module_type_cost),
                    basePrice=base_price,
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