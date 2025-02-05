from sqlmodel import Session, select
from app.models.module_set_option_types import ModuleSetOptionTypes
from app.models.option_type import OptionType
from app.models.module_set import ModuleSet
from fastapi import HTTPException
from typing import List, Tuple
from app.crud.base import CRUDBase

class ModuleSetOptionTypesCRUD(CRUDBase[ModuleSetOptionTypes]):
    def __init__(self): 
        super().__init__(ModuleSetOptionTypes, "module_set_id")

    def get_option_types_by_module_set(self, session: Session, module_set_id: int) -> List[Tuple[OptionType, ModuleSetOptionTypes]]:
        """ 모듈 세트 안에 포함된 옵션 타입들을 가져오는 기능 """
        statement = (
            select(OptionType, ModuleSetOptionTypes)
            .join(ModuleSetOptionTypes, OptionType.option_type_id == ModuleSetOptionTypes.option_type_id)
            .where(ModuleSetOptionTypes.module_set_id == module_set_id)
        )
        return list(session.exec(statement).all())

    def get_module_sets_by_option_type(self, session: Session, option_type_id: int) -> List[Tuple[ModuleSet, ModuleSetOptionTypes]]:
        """ 특정 옵션 타입이 포함된 모듈 세트들을 가져오는 기능 """
        statement = (
            select(ModuleSet, ModuleSetOptionTypes)
            .join(ModuleSetOptionTypes, ModuleSet.module_set_id == ModuleSetOptionTypes.module_set_id)
            .where(ModuleSetOptionTypes.option_type_id == option_type_id)
        )
        return list(session.exec(statement).all())

    def get_item_type_name(self, item_type_id: int) -> str:
        """
        모듈 세트 옵션 타입 관련 기능에서 사용될 수 있는 아이템 유형 이름을 반환합니다.
        """
        from app.crud.lut import get_item_type_mapping
        mapping = get_item_type_mapping()
        return mapping.get(item_type_id, "Unknown")

module_set_option_type_crud = ModuleSetOptionTypesCRUD()