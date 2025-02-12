from typing import List, Optional
from sqlmodel import Session
from app.api.schemas.admin.option_type_schema import OptionTypeItem, OptionTypeData, OptionTypeGetResponse, OptionTypeRegisterRequest, OptionTypeRegisterResponse, OptionTypeUpdateRequest, OptionTypeUpdateResponse, OptionTypeDeleteResponse
from app.core.s3_storage import list_files_by_category, upload_file_generic
from app.db.crud.option_type import option_type_crud
from app.db.models.option_type import OptionType
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime

class OptionTypeService:
    """옵션 타입 서비스"""
    
    def upload_optiontype_image(file_obj, optiontype_id: int, filename: Optional[str] = None) -> str:
        """
        옵션타입 이미지 업로드 함수.
        저장 경로: optiontype/{optiontype_id}/{filename}
        """
        return upload_file_generic(file_obj, "optiontype", optiontype_id, filename=filename, default_ext=".jpg")

    @staticmethod
    def list_optiontype_images(optiontype_id: int) -> list:
        """옵션 타입 이미지 목록 조회 함수"""
        return list_files_by_category("optiontype", optiontype_id)
      
    @staticmethod 
    def _save_option_type_images(option_type_images: List[str]) -> str:
        """옵션 타입 이미지 저장 후 이미지 경로 문자열 반환
           (저장 후 반환된 이미지 주소들을 콤마로 구분하여 DB에 저장)
        """
        saved_images = [OptionTypeService._save_image(image) for image in option_type_images]
        return ",".join(saved_images)
      
    @staticmethod
    def _parse_option_type_images(option_type_images: str) -> List[str]:
        """옵션 타입 이미지 문자열 파싱 후 리스트 반환"""
        return option_type_images.split(",")
    
    @staticmethod
    def _save_image(image: str) -> str:
        """이미지 저장 후 이미지 경로 반환"""
        return image  
    
    @staticmethod
    def _convert_model_to_schema(option_type: OptionType) -> OptionTypeItem:
        """옵션 타입 모델을 스키마로 변환"""
        if option_type.option_type_id is None:
            raise DatabaseError(
                message="Option type ID is required",
                detail={"option_type": option_type.dict()}
            )
            
        if option_type.option_type_images:
            option_type_images = OptionTypeService._parse_option_type_images(option_type.option_type_images)
        else:
            option_type_images = []
            
        return OptionTypeItem(
            option_type_id=option_type.option_type_id,
            option_type_name=option_type.option_type_name,
            option_type_size=option_type.option_type_size,
            option_type_cost=option_type.option_type_cost,
            description=option_type.description or "",
            option_type_images=option_type_images,
            option_type_features=option_type.option_type_features or "",
            created_at=option_type.created_at,
            created_by=option_type.created_by,
            updated_at=option_type.updated_at,
            updated_by=option_type.updated_by
        )
    
    @staticmethod
    def get_option_type_list(session: Session, page: int, page_size: int) -> OptionTypeGetResponse:
        """관리자 옵션 타입 목록 조회 서비스"""
        paginated_result = option_type_crud.paginate(session, page, page_size)
        option_types: List[OptionType] = paginated_result["items"]
        
        # 옵션 타입 데이터 변환
        option_type_items = [
            OptionTypeItem.parse_obj(
                OptionTypeService._convert_model_to_schema(option_type)
            )
            for option_type in option_types
        ]

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
    def register_option_type(session: Session, option_type_data: OptionTypeRegisterRequest, user_pk: int) -> OptionTypeRegisterResponse:
        """옵션 타입 등록 서비스"""
        
        imgUrl = ""
        images = option_type_data.option_type_images or []
        for image in images:
            imgUrl += OptionTypeService._save_image(image) + ","
            
        # 2. 새 옵션 타입 생성
        new_option_type = OptionType(
            option_type_name=option_type_data.option_type_name,
            option_type_size=option_type_data.option_type_size,
            option_type_cost=option_type_data.option_type_cost,
            description=option_type_data.description,
            option_type_images=imgUrl,
            option_type_features=option_type_data.option_type_features or "",
            created_at=datetime.now(),
            created_by=user_pk,
            updated_at=datetime.now(),
            updated_by=user_pk
        )
        
        option_type_crud.create(session, new_option_type)
        return OptionTypeRegisterResponse.success(
            message="Option type registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_option_type(
        session: Session,
        option_type_id: int,
        update_data: OptionTypeUpdateRequest,  # OptionTypeUpdateRequest 객체라고 가정
        user_pk: int
    ) -> OptionTypeUpdateResponse:
        # 기존에 등록된 옵션 타입 객체를 조회합니다.
        option_type = session.get(OptionType, option_type_id)
        if not option_type:
            raise NotFoundError(
                message="Option type not found",
                detail={"option_type_id": option_type_id}
            )
      
        # 클라이언트가 전달한 변경된 필드만 기존 객체에 업데이트합니다.
        update_fields = update_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            if key == "option_type_images" and value is not None:
                value = OptionTypeService._save_option_type_images(value)
            setattr(option_type, key, value)
        
        # 업데이트 정보 갱신
        option_type.updated_by = user_pk
        option_type.updated_at = datetime.now()
        
        session.commit()
        session.refresh(option_type)
        
        # 업데이트 성공 후 등록된 옵션 타입의 id를 응답에 포함합니다.
        return OptionTypeUpdateResponse.success(
            message="Option type updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_option_type(session: Session, option_type_id: int, user_pk: int) -> OptionTypeDeleteResponse:
        """옵션 타입 삭제 서비스"""
        # 옵션 타입 존재 여부 확인
        option_type = option_type_crud.get_by_field(session, option_type_id, "option_type_id")
        if not option_type:
            raise NotFoundError(
                message="Option type not found",
                detail={"option_type_id": option_type_id}
            )

        # 옵션 타입 삭제
        option_type_crud.soft_delete(session, option_type_id, "option_type_id")

        return OptionTypeDeleteResponse.success(
            message="Option type deleted successfully"
        )   
