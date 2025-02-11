from sqlmodel import Session, select
from app.db.models.module_set import ModuleSet
from app.db.crud.base import CRUDBase

class ModuleSetCRUD(CRUDBase[ModuleSet]):
    def __init__(self):
        super().__init__(ModuleSet)

    def get_by_name(self, session: Session, module_set_name: str):
        """
        모듈 세트 이름으로 모듈 세트를 조회합니다.

        Args:
            session (Session): DB 세션
            module_set_name (str): 모듈 세트 이름
      
        Returns:
            ModuleSet: 조회된 모듈 세트 객체

        Raises:
            NotFoundError: 해당 이름의 모듈 세트가 없는 경우
            DatabaseError: DB 조회 중 오류 발생 시
        """
        statement = select(self.model).where(self.model.module_set_name == module_set_name)
        return session.exec(statement).first()

    def calculate_base_price(self, session: Session, module_set_id: int) -> float:
        """
        모듈 세트의 기본 가격 계산:
          - 모듈 타입의 기본 비용 + 해당 모듈 세트에 포함된 옵션들의 추가 비용 합산
        """
        # 1. 모듈 세트 조회
        module_set = self.get_by_field(session, module_set_id, "module_set_id")
        if not module_set:
            raise Exception(f"Module set not found for id {module_set_id}")
        
        # 2. 모듈 타입 비용 조회 (module_type_crud에서 모듈 타입 정보를 가져옴)
        from app.db.crud.lut import module_type as module_type_crud
        module_type_info = module_type_crud.get_by_id(session, module_set.module_type_id)
        if not module_type_info:
            raise Exception(f"Module type not found for id {module_set.module_type_id}")
        
        base_cost = float(module_type_info.module_type_cost)
        
        # 3. 모듈 세트에 속한 옵션들의 추가 비용 계산
        from app.db.crud.module_set_option_type import module_set_option_type_crud
        from app.db.crud.option_type import option_type_crud
        option_data = module_set_option_type_crud.get_option_types_by_module_set(session, module_set_id)
        option_items = option_data.get("items", [])
        option_cost = sum(
            float(option_type_crud.get_option_cost_by_id(session, opt.option_type_id)) * (opt.option_quantity or 1)
            for opt in option_items
        )
        
        return base_cost + option_cost

module_set_crud = ModuleSetCRUD()
