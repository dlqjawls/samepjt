from typing import List, Optional
from sqlmodel import Session, select
from app.db.models.module_set import ModuleSet
from app.db.crud.base import CRUDBase
from app.db.crud.module_set_option_type import module_set_option_type_crud
from app.db.crud.option_type import option_type_crud
from app.db.crud.lut import module_type as module_type_crud

class ModuleSetCRUD(CRUDBase[ModuleSet]):
    def __init__(self):
        super().__init__(ModuleSet)
        
    def get_by_id(self, session: Session, module_set_id: int) -> Optional[ModuleSet]:
        """모듈 세트 ID로 모듈 세트를 조회합니다."""
        statement = select(self.model).where(self.model.module_set_id == module_set_id)
        return session.exec(statement).first()

    def get_by_name(self, session: Session, module_set_name: str) -> Optional[ModuleSet]:
        """모듈 세트 이름으로 모듈 세트를 조회합니다."""
        statement = select(self.model).where(self.model.module_set_name == module_set_name)
        return session.exec(statement).first()

    def calculate_base_price(self, session: Session, module_set_id: int) -> float:
        """모듈 세트의 기본 가격 계산: 모듈 타입의 기본 비용 + 해당 모듈 세트에 포함된 옵션들의 추가 비용 합산"""
        # 모듈 세트 조회
        module_set = self.get_by_id(session, module_set_id)
        if not module_set:
            raise Exception(f"Module set not found for id {module_set_id}")
        
        # 모듈 타입 비용 조회
        module_type_info = module_type_crud.get_by_id(session, module_set.module_type_id)
        if not module_type_info:
            raise Exception(f"Module type not found for id {module_set.module_type_id}")
        
        base_cost = float(module_type_info.module_type_cost)
        
        # 모듈 세트에 속한 옵션들의 추가 비용 계산
        option_items = module_set_option_type_crud.get_option_types_by_module_set(session, module_set_id)
        option_cost = sum(
            float(option_type_crud.get_option_cost_by_id(session, opt.option_type_id) or 0) * (opt.option_quantity or 1)  
            for opt in option_items
        )
        
        return base_cost + option_cost
      
module_set_crud = ModuleSetCRUD()
