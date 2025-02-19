from typing import List, Optional
from fastapi import UploadFile
from sqlmodel import Session
from app.api.schemas.admin.module_set_schema import ModuleSetItem, ModuleSetData, ModuleSetGetResponse, ModuleSetOptionType, ModuleSetRegisterRequest, ModuleSetMessageResponse, ModuleSetUpdateRequest, ModuleSetAddOptionRequest, ModuleSetRemoveImageRequest
from app.core import s3_storage
from app.db.crud.module_set import module_set_crud
from app.db.models.module_set import ModuleSet
from app.db.models.module_set_option_types import ModuleSetOptionTypes
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from app.db.crud.lut import module_type as module_type_crud
from app.db.crud.module_set_option_type import module_set_option_type_crud
from app.db.crud.option_type import option_type_crud

class ModuleSetService:
    
    @staticmethod
    def _get_module_set_or_raise(session: Session, module_set_id: int) -> ModuleSet:
        """모듈 세트 존재 여부 확인"""
        module_set = module_set_crud.get_by_id(session, module_set_id)
        if not module_set:
            raise NotFoundError(
                message="Module set not found",
                detail={"module_set_id": module_set_id}
            )
        return module_set 


    @staticmethod
    def _check_module_type_exists(session: Session, module_type_id: int) -> None:
        """모듈 타입 존재 여부 확인"""
        if not module_type_crud.get_by_id(session, module_type_id):
            raise NotFoundError(
                message="Module type not found",
                detail={"module_type_id": module_type_id}
            )
            
    @staticmethod 
    def _check_option_type_exists(session: Session, option_type_id: int) -> None:
        """옵션 타입 존재 여부 확인"""
        if not module_set_option_type_crud.get_by_field(session, option_type_id, "option_type_id"):
            raise NotFoundError(
                message="Option type not found",
                detail={"option_type_id": option_type_id}
            )
    
    @staticmethod
    def _save_module_set_images(module_set_images: UploadFile, module_set_id: int) -> str:
        """모듈 세트 이미지 저장 후 이미지 경로 문자열 반환"""
        content_type = module_set_images.content_type if module_set_images.content_type else "image/jpeg"
        print(content_type)
        saved_images = s3_storage.upload_file_generic(
            module_set_images.file,
            "moduletype",
            module_set_id,
            filename=module_set_images.filename,
            default_ext=".jpg",
            ExtraArgs={"ACL": "public-read", "ContentType": content_type}
        )
        return saved_images

    @staticmethod
    def _parse_module_set_images(module_set_images: str) -> List[str]:
        """모듈 세트 이미지 문자열 파싱 후 리스트 반환"""
        return module_set_images.split(",")

    @staticmethod
    def get_module_set_list(session: Session, page: int, page_size: int) -> ModuleSetGetResponse:
        """모듈 세트 목록 조회"""
        
        # 모듈 세트 목록 조회
        paginated_result = module_set_crud.paginate(session, page, page_size)
        module_sets: List[ModuleSet] = paginated_result["items"]
        
        # 모듈 세트 데이터 리스트 생성
        module_set_items = []
        for module_set in module_sets:

            # 모듈 세트 ID 확인
            if module_set.module_set_id is None:
                raise DatabaseError(
                    message="Module set auto increment ID is not assigned",
                    detail={"module_set_id": module_set.module_set_id}
                )
            
            # 모듈 타입 존재 여부 확인
            ModuleSetService._check_module_type_exists(session, module_set.module_type_id)
            
            # 모듈 세트 가격 계산
            calculated_cost = module_set_crud.calculate_base_price(
                session, 
                module_set.module_set_id, 
            )
            
            # 모듈 세트 이미지 파싱
            if module_set.module_set_images:
                module_set_images = ModuleSetService._parse_module_set_images(module_set.module_set_images)
            else:
                module_set_images = []
            
            # 모듈 세트 옵션 타입 조회
            module_set_option_types : List[ModuleSetOptionType] = [
                ModuleSetOptionType(
                    option_type_id=option_type.option_type_id,
                    option_type_name=option_type_crud.get_option_name_by_id(session, option_type.option_type_id),
                    quantity=option_type.option_quantity
                ) for option_type in module_set_option_type_crud.get_option_types_by_module_set(session, module_set.module_set_id)
            ]
            
            # 모듈 세트 데이터 변환
            schema_obj = ModuleSetItem(
                module_set_id=module_set.module_set_id,
                module_set_name=module_set.module_set_name,
                description=module_set.description or "",
                module_set_images=module_set_images,
                module_set_features=module_set.module_set_features or "",
                module_type_id=module_set.module_type_id,
                cost=calculated_cost,
                module_set_option_types=module_set_option_types,
                created_at=module_set.created_at,
                created_by=module_set.created_by,
                updated_at=module_set.updated_at,
                updated_by=module_set.updated_by
            )
            
            # 모듈 세트 데이터 리스트에 추가
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
    def register_module_set(session: Session, module_set_data: ModuleSetRegisterRequest, user_pk: int) -> ModuleSetMessageResponse:
        """모듈 세트 등록"""
        
        # 모듈 타입 존재 여부 확인
        ModuleSetService._check_module_type_exists(session, module_set_data.module_type_id)
        
        # 새로운 모듈 세트 생성 (이미지 빈 문자열로 처리)
        new_module_set: ModuleSet = ModuleSet(
            module_set_name=module_set_data.module_set_name,
            description=module_set_data.description,
            module_set_images="",
            module_set_features=module_set_data.module_set_features,
            module_type_id=module_set_data.module_type_id,
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 모듈 세트 생성
        new_module_set = module_set_crud.create(session, new_module_set)

        return ModuleSetMessageResponse.success(
            message="Module set registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_module_set(
        session: Session,
        module_set_id: int,
        module_set_data: ModuleSetUpdateRequest,
        user_pk: int
    ) -> ModuleSetMessageResponse:
        """모듈 세트 수정"""
        
        module_set = ModuleSetService._get_module_set_or_raise(session, module_set_id)

        # 모듈 타입이 변경되는 경우에만 존재 여부 확인
        if module_set_data.module_type_id:
            ModuleSetService._check_module_type_exists(session, module_set_data.module_type_id)

        update_data = module_set_data.dict(exclude_unset=True)
        update_data["updated_by"] = user_pk
        update_data["updated_at"] = datetime.now()

        module_set_crud.update(session, module_set_id, update_data, "module_set_id")
        return ModuleSetMessageResponse.success(
            message="Module set updated successfully"
        )
   
        
    @staticmethod
    @handle_transaction
    def delete_module_set(session: Session, module_set_id: int, user_pk: int) -> ModuleSetMessageResponse:
        """모듈 세트 삭제 서비스"""
        
        # 모듈 세트 존재 여부 확인
        ModuleSetService._get_module_set_or_raise(session, module_set_id)

        # 연결된 옵션 타입 삭제
        module_set_option_type_crud.delete_by_module_set_id(session, module_set_id)

        # 모듈 세트 삭제
        module_set_crud.soft_delete(session, module_set_id, "module_set_id")

        return ModuleSetMessageResponse.success(
            message="Module set deleted successfully"
        )
        
        
    @staticmethod
    @handle_transaction
    def add_module_set_image(session: Session, module_set_id: int, module_set_images: UploadFile) -> ModuleSetMessageResponse:
        """모듈 세트 이미지 추가"""
        # 모듈 세트 존재 여부 확인
        module_set = ModuleSetService._get_module_set_or_raise(session, module_set_id)
        
        # 모듈 세트 이미지 추가
        new_image_url = ModuleSetService._save_module_set_images(module_set_images, module_set_id)
        
        existing_images = module_set.module_set_images
        
        # 모듈 세트 이미지 업데이트
        if existing_images:
            existing_images = existing_images + "," + new_image_url
        else:
            existing_images = new_image_url
        
        module_set_crud.update(session, module_set_id, {"module_set_images": existing_images}, id_field="module_set_id")

        return ModuleSetMessageResponse.success(
            message="Module set image added successfully" 
        )
    
    @staticmethod
    @handle_transaction
    def remove_module_set_image(session: Session, module_set_id: int, request: ModuleSetRemoveImageRequest) -> ModuleSetMessageResponse:
        """모듈 세트 이미지 삭제"""
        
        # 모듈 세트 존재 여부 확인
        module_set = ModuleSetService._get_module_set_or_raise(session, module_set_id)
      
        if module_set.module_set_images:
            # 모듈 세트 이미지 파싱
            existing_images = ModuleSetService._parse_module_set_images(module_set.module_set_images)

            # 이미지 삭제
            existing_images.remove(request.image_url)
            
            # 모듈 세트 이미지 업데이트
            image_urls = ",".join(existing_images)
            module_set_crud.update(session, module_set_id, {"module_set_images": image_urls}, id_field="module_set_id")
        
        return ModuleSetMessageResponse.success(
            message="Module set image removed successfully"
        )
    
    @staticmethod
    @handle_transaction
    def add_module_set_option(session: Session, module_set_id: int, request: ModuleSetAddOptionRequest) -> ModuleSetMessageResponse:
        """모듈 세트 옵션 추가"""
        # 모듈 세트 존재 여부 확인
        module_set = ModuleSetService._get_module_set_or_raise(session, module_set_id)
        
        # 옵션 타입 존재 여부 확인
        ModuleSetService._check_option_type_exists(session, request.option_type_id)

        # 모듈 세트 옵션 추가
        module_set_option_type_crud.create(session, ModuleSetOptionTypes(module_set_id=module_set_id, option_type_id=request.option_type_id, option_quantity=request.quantity))

        return ModuleSetMessageResponse.success(
            message="Module set option added successfully"
        )
      
    @staticmethod
    @handle_transaction
    def remove_module_set_option(session: Session, module_set_id: int, option_type_id: int) -> ModuleSetMessageResponse:
        """모듈 세트 옵션 삭제"""
        # 모듈 세트 존재 여부 확인
        module_set = ModuleSetService._get_module_set_or_raise(session, module_set_id)
        
        # 옵션 타입 존재 여부 확인
        ModuleSetService._check_option_type_exists(session, option_type_id)

        # 모듈 세트 옵션 삭제
        module_set_option_type_crud.delete_by_module_set_id_and_option_type_id(session, module_set_id, option_type_id)

        return ModuleSetMessageResponse.success(
            message="Module set option removed successfully"
        )