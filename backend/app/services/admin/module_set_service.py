from typing import List, Optional
from fastapi import UploadFile
from sqlmodel import Session
from app.api.schemas.admin.module_set_schema import ModuleSetItem, ModuleSetData, ModuleSetGetResponse, ModuleSetOptionType, ModuleSetRegisterRequest, ModuleSetRegisterResponse, ModuleSetUpdateRequest, ModuleSetUpdateResponse, ModuleSetDeleteResponse
from app.core import s3_storage
from app.db.crud.module_set import module_set_crud
from app.db.models.module_set import ModuleSet
from app.db.models.module_set_option_types import ModuleSetOptionTypes
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from app.db.crud.lut import module_type as module_type_crud
from app.db.crud.module_set_option_type import module_set_option_type_crud

class ModuleSetService:
    
    @staticmethod
    def upload_moduletype_image(file_obj, moduletype_id: int, filename: Optional[str] = None) -> str:
        """모듈타입 이미지 업로드 함수"""
        return s3_storage.upload_file_generic(file_obj, "moduletype", moduletype_id, filename=filename, default_ext=".jpg")

    @staticmethod
    def list_moduletype_images(moduletype_id: int) -> list:
        """주어진 모듈타입 ID의 모든 이미지를 조회합니다. 없으면 []를 반환합니다."""
        return s3_storage.list_files_by_category("moduletype", moduletype_id)
      
    @staticmethod
    def _check_module_type_exists(session: Session, module_type_id: int) -> None:
        """모듈 타입 존재 여부 확인"""
        if not module_type_crud.get_by_id(session, module_type_id):
            raise NotFoundError(
                message="Module type not found",
                detail={"module_type_id": module_type_id}
            )
            
    @staticmethod
    def _save_module_set_images(module_set_images: List[UploadFile], module_set_id: int) -> str:
        """모듈 세트 이미지 저장 후 이미지 경로 문자열 반환"""
        saved_images = [s3_storage.upload_moduletype_image(image.file, module_set_id, filename=image.filename) for image in module_set_images]

        return ",".join(saved_images)

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
            
            # 모듈 세트 ID 존재 여부 확인
            if module_set.module_set_id is None:
                raise DatabaseError(
                    message="Module set ID is required",
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
                    option_type_id=option_type["id"],
                    option_type_name=option_type["name"],
                    quantity=option_type["quantity"]
                ) for option_type in module_set_crud.get_option_types(session, module_set.module_set_id)
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
    def register_module_set(session: Session, module_set_data: ModuleSetRegisterRequest, user_pk: int) -> ModuleSetRegisterResponse:
        """모듈 세트 등록"""
        
        # 모듈 타입 존재 여부 확인
        ModuleSetService._check_module_type_exists(session, module_set_data.module_type_id)

        # 새로운 모듈 세트를 DB에 먼저 생성 (이미지 빈 문자열로 처리)
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
        
        # new_module_set.module_set_id 할당
        new_module_set = module_set_crud.create(session, new_module_set)
        if new_module_set.module_set_id is None:
            raise DatabaseError(
                message="Module set auto increment ID is not assigned"
            )

        # 모듈 세트 이미지 첨부가 있는 경우, 새 module_set_id 경로로 이미지를 저장하고, 이미지 URL 리스트를 DB에 업데이트
        if module_set_data.module_set_images:
            processed_images = ModuleSetService._save_module_set_images(module_set_data.module_set_images, new_module_set.module_set_id)
            new_module_set.module_set_images = processed_images
            module_set_crud.update(session, new_module_set.module_set_id, {"module_set_images": processed_images}, id_field="module_set_id")

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
        """모듈 세트 수정"""
        
        # 모듈 세트 존재 여부 확인
        module_set = module_set_crud.get_by_field(session, module_set_id, "module_set_id")
        if not module_set or module_set.module_set_id is None:
            raise NotFoundError(
                message="Module set not found",
                detail={"module_set_id": module_set_id}
            )

        # module_type_id가 업데이트 대상에 포함되었다면 존재 여부 확인
        if update_data.module_type_id is not None:
            ModuleSetService._check_module_type_exists(session, update_data.module_type_id)

        # 옵션 데이터는 별도로 추출 (옵션 변경이 있을 경우 모듈세트옵션타입 DB에 반영)
        new_options = update_data.options if update_data.options is not None else None

        # 업데이트할 데이터 추출 (옵션 필드는 제외)
        update_fields = update_data.dict(exclude_unset=True)
        if "options" in update_fields:
            del update_fields["options"]

        # 이미지 파일이 제공된 경우 처리: S3 업로드 후 변환된 이미지 경로를 update_fields에 반영
        if "module_set_images" in update_fields and update_fields["module_set_images"]:
            processed_images = ModuleSetService._save_module_set_images(update_fields["module_set_images"], module_set.module_set_id)
            update_fields["module_set_images"] = processed_images

        # 업데이트 정보 갱신
        update_fields["updated_by"] = user_pk
        update_fields["updated_at"] = datetime.now()

        # 모듈 세트 기본 정보 업데이트
        module_set_crud.update(session, module_set.module_set_id, update_fields, id_field="module_set_id")

        # 옵션 타입 업데이트: 옵션 데이터가 제공되면 기존 옵션 데이터를 모두 삭제 후 신규 옵션 데이터를 추가
        if new_options is not None:
            # 기존 모듈세트옵션타입 삭제
            module_set_option_type_crud.delete_by_module_set_id(session, module_set.module_set_id)
            # 새로운 옵션들 추가
            for opt in new_options:
                new_option_record = ModuleSetOptionTypes(
                    module_set_id=module_set.module_set_id,
                    option_type_id=opt.optionTypeId,
                    option_quantity=opt.quantity,
                )
                module_set_option_type_crud.create(session, new_option_record)

        return ModuleSetUpdateResponse.success(
            message="Module set updated successfully"
        )
   
        
    @staticmethod
    @handle_transaction
    def delete_module_set(session: Session, module_set_id: int, user_pk: int) -> ModuleSetDeleteResponse:
        """모듈 세트 삭제 서비스"""
        # 모듈 세트 존재 여부 확인
        module_set = module_set_crud.get_by_field(session, module_set_id, "module_set_id")
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