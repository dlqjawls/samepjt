from typing import List, Optional
from fastapi import UploadFile
from sqlmodel import Session
from app.api.schemas.admin.option_type_schema import OptionTypeItem, OptionTypeData, OptionTypeGetResponse, OptionTypeRegisterRequest, OptionTypeMessageResponse, OptionTypeUpdateRequest, OptionTypeRemoveImageRequest  
from app.core import s3_storage
from app.db.crud.option_type import option_type_crud
from app.db.models.option_type import OptionType
from app.db.crud.module_set_option_type import module_set_option_type_crud
from app.db.crud.option import option_crud
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime

class OptionTypeService:
    """옵션 타입 서비스"""
    
    @staticmethod
    def _get_option_type_or_raise(session: Session, option_type_id: int) -> OptionType:
        """옵션 타입 존재 여부 확인"""
        option_type = option_type_crud.get_by_id(session, option_type_id)
        if not option_type:
            raise NotFoundError(
                message="Option type not found",
                detail={"option_type_id": option_type_id}
            )   
        return option_type
            
    @staticmethod
    def list_optiontype_images(optiontype_id: int) -> list:
        """옵션 타입 이미지 목록 조회 함수"""
        return s3_storage.list_files_by_category("optiontype", optiontype_id)
      
    @staticmethod
    def _save_option_type_images(option_type_images: UploadFile, option_type_id: int) -> str:
        """옵션 타입 이미지 저장 후 이미지 경로 문자열 반환"""
        saved_images = s3_storage.upload_file_generic(option_type_images.file, "optiontype", option_type_id, filename=option_type_images.filename, default_ext=".jpg", ExtraArgs={"ACL": "public-read", "ContentType": "image/jpeg"})
        return saved_images
      
    @staticmethod
    def _parse_option_type_images(option_type_images: str) -> List[str]:
        """옵션 타입 이미지 문자열 파싱 후 리스트 반환"""
        return option_type_images.split(",")
    
    @staticmethod
    def get_option_type_list(session: Session, page: int, page_size: int) -> OptionTypeGetResponse:
        """옵션 타입 목록 조회 서비스"""
        
         
        # 옵션 타입 목록 조회
        paginated_result = option_type_crud.paginate(session, page, page_size)
        option_types: List[OptionType] = paginated_result["items"]
        
        # 옵션 타입 데이터 리스트 생성
        option_type_items = []
        for option_type in option_types:

            # 옵션 타입 ID 확인
            if option_type.option_type_id is None:
                raise DatabaseError(
                    message="Option type auto increment ID is not assigned",
                    detail={"option_type_id": option_type.option_type_id}
                )
                
            # 옵션 타입 이미지 파싱
            if option_type.option_type_images:
                option_type_images = OptionTypeService._parse_option_type_images(option_type.option_type_images)
            else:
                option_type_images = []
          
            
            # 옵션 타입 데이터 변환
            schema_obj = OptionTypeItem(
                option_type_id=option_type.option_type_id,
                option_type_name=option_type.option_type_name,
                description=option_type.description or "",
                option_type_images=option_type_images,
                option_type_features=option_type.option_type_features or "",
                option_type_size=option_type.option_type_size,
                option_type_cost=option_type.option_type_cost,
                created_at=option_type.created_at,
                created_by=option_type.created_by,
                updated_at=option_type.updated_at,
                updated_by=option_type.updated_by
            )
            
            # 옵션 타입 데이터 리스트에 추가
            option_type_items.append(schema_obj)

        option_type_data = OptionTypeData(
            option_types=option_type_items,
            pagination=paginated_result["pagination"]
        )


        return OptionTypeGetResponse.success(
            data=option_type_data,
            message="Option type data retrieved successfully"
        )

    @staticmethod
    @handle_transaction
    def register_option_type(session: Session, option_type_data: OptionTypeRegisterRequest, user_pk: int) -> OptionTypeMessageResponse:
        """옵션 타입 등록 서비스"""
      
        # 새 옵션 타입 생성
        new_option_type = OptionType(
            option_type_name=option_type_data.option_type_name,
            option_type_size=option_type_data.option_type_size,
            option_type_cost=option_type_data.option_type_cost,
            description=option_type_data.description,
            option_type_images="",
            option_type_features=option_type_data.option_type_features,
            created_at=datetime.now(),
            created_by=user_pk,
            updated_at=datetime.now(),
            updated_by=user_pk
        )
        
        # 옵션 타입 생성
        new_option_type = option_type_crud.create(session, new_option_type)
        
        return OptionTypeMessageResponse.success(
            message="Option type registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_option_type(
        session: Session,
        option_type_id: int,
        option_type_data: OptionTypeUpdateRequest,
        user_pk: int
    ) -> OptionTypeMessageResponse:
        # 기존에 등록된 옵션 타입 객체를 조회합니다.
        option_type = OptionTypeService._get_option_type_or_raise(session, option_type_id)
      
        update_data = option_type_data.dict(exclude_unset=True)  
        update_data["updated_by"] = user_pk
        update_data["updated_at"] = datetime.now()  
        
        option_type_crud.update(session, option_type_id, update_data, "option_type_id")
        
        return OptionTypeMessageResponse.success(
            message="Option type updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_option_type(session: Session, option_type_id: int, user_pk: int) -> OptionTypeMessageResponse:
        """옵션 타입 삭제 서비스"""
        # 옵션 타입 존재 여부 확인
        OptionTypeService._get_option_type_or_raise(session, option_type_id)

        # 연결된 모듈 세트 조회
        module_sets = module_set_option_type_crud.get_module_sets_by_option_type(session, option_type_id)
        if module_sets:
            raise DatabaseError(
                message="Option type is associated with module sets",
                detail={"option_type_id": option_type_id}
            )
            
        # 연결된 옵션 조회
        options = option_crud.get_options_by_type(session, option_type_id)
        if options:
            raise DatabaseError(
                message="Option type is associated with options",
                detail={"option_type_id": option_type_id}
            )
            
        # 옵션 타입 삭제
        option_type_crud.soft_delete(session, option_type_id, "option_type_id")

        return OptionTypeMessageResponse.success(
            message="Option type deleted successfully"
        )   

    @staticmethod
    @handle_transaction
    def add_option_type_image(session: Session, option_type_id: int, option_type_images: UploadFile) -> OptionTypeMessageResponse:
        """옵션 타입 이미지 추가 서비스"""
        # 옵션 타입 존재 여부 확인
        option_type = OptionTypeService._get_option_type_or_raise(session, option_type_id)

        # 옵션 타입 이미지 추가
        new_image_url = OptionTypeService._save_option_type_images(option_type_images, option_type_id)
        
        existing_images = option_type.option_type_images  
        
        # 옵션 타입 이미지 업데이트
        if existing_images:
            existing_images = existing_images + "," + new_image_url
        else:
            existing_images = new_image_url 
            
        # 옵션 타입 이미지 업데이트
        option_type_crud.update(session, option_type_id, {"option_type_images": existing_images}, "option_type_id")
        
        return OptionTypeMessageResponse.success(
            message="Option type image added successfully"
        ) 
        
    @staticmethod
    @handle_transaction
    def remove_option_type_image(session: Session, option_type_id: int, request: OptionTypeRemoveImageRequest) -> OptionTypeMessageResponse:
        """옵션 타입 이미지 삭제"""
        
        # 옵션 타입 존재 여부 확인
        option_type = OptionTypeService._get_option_type_or_raise(session, option_type_id)
      
        if option_type.option_type_images:
            # 옵션 타입 이미지 파싱
            existing_images = OptionTypeService._parse_option_type_images(option_type.option_type_images)

            # 이미지 삭제
            existing_images.remove(request.image_url)
            
            # 옵션 타입 이미지 업데이트
            image_urls = ",".join(existing_images)
            option_type_crud.update(session, option_type_id, {"option_type_images": image_urls}, id_field="option_type_id")
        
        return OptionTypeMessageResponse.success(
            message="Option type image removed successfully"
        )    
        
    