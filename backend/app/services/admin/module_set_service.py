from typing import List
from sqlmodel import Session
from app.api.schemas.admin.module_set_schema import ModuleSetItem, ModuleSetData, ModuleSetGetResponse, ModuleSetRegisterRequest, ModuleSetRegisterResponse, ModuleSetUpdateRequest, ModuleSetUpdateResponse, ModuleSetDeleteResponse
from app.db.crud.module_set import module_set_crud
from app.db.models.module_set import ModuleSet
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from app.db.crud.lut import module_type as module_type_crud

class ModuleSetService:
    
    @staticmethod
    def _check_module_type_exists(session: Session, module_type_id: int) -> None:
        """모듈 타입 존재 여부 확인"""
        if not module_type_crud.get_by_id(session, module_type_id):
            raise NotFoundError(
                message="Module type not found",
                detail={"module_type_id": module_type_id}
            )
            
    @staticmethod
    def _save_module_set_images(module_set_images: List[str]) -> str:
        """모듈 세트 이미지 저장 후 이미지 경로 문자열 반환
           (저장 후 반환된 이미지 주소들을 콤마로 구분하여 DB에 저장)
        """
        saved_images = [ModuleSetService._save_image(image) for image in module_set_images]
        return ",".join(saved_images)

    @staticmethod
    def _parse_module_set_images(module_set_images: str) -> List[str]:
        """모듈 세트 이미지 문자열 파싱 후 리스트 반환"""
        return module_set_images.split(",")

    @staticmethod
    def _save_image(image: str) -> str:
        """이미지 저장 후 이미지 경로 반환 (단순히 원본 문자열 반환)"""
        return image
        
    @staticmethod
    def _convert_model_to_schema(module_set: ModuleSet) -> ModuleSetItem:
        """모듈 세트 데이터 변환"""
        if module_set.module_set_id is None:
            raise DatabaseError(
                message="Module set ID is required",
                detail={"module_set": module_set.dict()}
            )
            
        if module_set.module_set_images:
            module_set_images = ModuleSetService._parse_module_set_images(module_set.module_set_images)
        else:
            module_set_images = []
            
        return ModuleSetItem(
            module_set_id=module_set.module_set_id,
            module_set_name=module_set.module_set_name,
            description=module_set.description or "", 
            module_set_images=module_set_images,
            module_set_features=module_set.module_set_features or "",
            module_type_id=module_set.module_type_id,
            cost=0,
            created_at=module_set.created_at,
            created_by=module_set.created_by,
            updated_at=module_set.updated_at,
            updated_by=module_set.updated_by

        )
    
        
    @staticmethod
    def schema_to_model(register_request: ModuleSetRegisterRequest, user_pk: int) -> ModuleSet:
        """모듈 세트 등록 요청 스키마를 ModuleSet 모델로 변환"""
        images = register_request.module_set_images or []
        processed_images = ModuleSetService._save_module_set_images(images)
        return ModuleSet(
            module_set_name=register_request.module_set_name,
            description=register_request.description or "",
            module_set_images=processed_images,
            module_set_features=register_request.module_set_features or "",
            module_type_id=register_request.module_type_id,
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )   
        
    @staticmethod
    def _calculate_option_cost(session: Session, module_set_id: int) -> float:
        """모듈 세트에 포함된 옵션들의 비용 합산"""
        from app.db.crud.module_set_option_type import module_set_option_type_crud
        from app.db.crud.option_type import option_type_crud
        option_types = module_set_option_type_crud.get_option_types_by_module_set(session, module_set_id)["items"]
        return sum(option_type_crud.get_option_cost_by_id(session, opt.option_type_id) * (opt.option_quantity or 1) for opt in option_types)

    @staticmethod
    def _calculate_base_price(session: Session, module_set_id: int, module_type_cost: float) -> float:
        """모듈 세트의 기본 가격 계산 (모듈 타입 비용 + 옵션 비용)"""
        return module_type_cost + ModuleSetService._calculate_option_cost(session, module_set_id)

    @staticmethod
    def get_module_set_list(session: Session, page: int, page_size: int) -> ModuleSetGetResponse:
        """관리자 모듈 세트 목록 조회 서비스"""
        paginated_result = module_set_crud.paginate(session, page, page_size)
        module_sets: List[ModuleSet] = paginated_result["items"]
        
        # 모듈 세트 데이터 변환 후 가격 계산 적용
        module_set_items = []
        for module_set in module_sets:
            module_type_info = module_type_crud.get_by_id(session, module_set.module_type_id)
            if not module_type_info:
                raise DatabaseError(
                    message="Module type not found",
                    detail={"module_type_id": module_set.module_type_id}
                )
            calculated_cost = ModuleSetService._calculate_base_price(
                session, 
                module_set.module_set_id, 
                float(module_type_info.module_type_cost)
            )
            schema_obj = ModuleSetService._convert_model_to_schema(module_set)
            schema_obj.cost = calculated_cost
            module_set_items.append(schema_obj)

        module_set_data = ModuleSetData(
            module_sets=module_set_items,
            pagination=paginated_result["pagination"]
        )

        return ModuleSetGetResponse.success(
            data=module_set_data,
            message="Module set data retrieved successfully"
        )

    @staticmethod
    @handle_transaction
    def register_module_set(session: Session, module_set_data: ModuleSetRegisterRequest, user_pk: int) -> ModuleSetRegisterResponse:
        """모듈 세트 등록 서비스"""
        # 1. 모듈 타입 존재 여부 확인
        ModuleSetService._check_module_type_exists(session, module_set_data.module_type_id)

        # 2. 새 모듈 세트 생성
        new_module_set = ModuleSet(
            module_set_name=module_set_data.module_set_name,
            description=module_set_data.description,
            module_set_images=module_set_data.module_set_images,
            module_set_features=module_set_data.module_set_features,
            module_type_id=module_set_data.module_type_id,
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        module_set_crud.create(session, new_module_set)
        return ModuleSetRegisterResponse.success(
            message="Module set registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_module_set(
        session: Session,
        module_set_id: int,
        update_data: ModuleSetUpdateRequest,
        user_pk: int
    ) -> ModuleSetUpdateResponse:
        # 기존에 등록된 모듈 세트 객체를 조회합니다.
        module_set = session.get(ModuleSet, module_set_id)
        if not module_set or module_set.deleted_at or update_data.module_type_id is None: 
            raise NotFoundError(
                message="Module set not found",
                detail={"module_set_id": module_set_id}
            )            
        
        # 모듈 타입 존재 여부 확인
        ModuleSetService._check_module_type_exists(session, update_data.module_type_id)
  
        # 클라이언트가 전달한 변경된 필드만 기존 객체에 업데이트합니다.
        update_fields = update_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            setattr(module_set, key, value)
        
        # 업데이트 정보 갱신
        module_set.updated_by = user_pk
        module_set.updated_at = datetime.now()
        
        session.commit()
        session.refresh(module_set)
        
        # 업데이트 성공 후 등록된 모듈 세트의 id를 응답에 포함합니다.
        return ModuleSetUpdateResponse.success(
            message="Module set updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_module_set(session: Session, module_set_id: int, user_pk: int) -> ModuleSetDeleteResponse:
        """모듈 세트 삭제 서비스"""
        # 모듈 세트 존재 여부 확인
        module_set = module_set_crud._get_by_field(session, module_set_id, "module_set_id")
        if not module_set:
            raise NotFoundError(
                message="Module set not found",
                detail={"module_set_id": module_set_id}
            )

        # 모듈 세트 삭제
        module_set_crud.soft_delete(session, module_set_id, "module_set_id")

        return ModuleSetDeleteResponse.success(
            message="Module set deleted successfully"
        )