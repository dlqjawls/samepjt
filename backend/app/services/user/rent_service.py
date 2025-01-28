from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from app.models.option import Option
from app.models.rent_history import RentHistory
from app.models.usage_history import UsageHistory
from app.api.schemas.user.rent import CancelRentRequest, RentRequest, RentResponse, CancelRentResponse, SelectedOptionType
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError
from app.utils.handle_transaction import handle_transaction
from app.crud.rent_history import rent_history_crud
from app.crud.vehicle import vehicle_crud
from app.crud.module import module_crud
from app.crud.option import option_crud
from app.crud.usage_history import usage_history_crud


class RentService:
    # TODO:LUT 조회 구현(하드코딩)
    # ITEM TYPE ID
    VEHICLE = 1
    MODULE = 2
    OPTION = 3

    # ITEM STATUS ID
    ACTIVE = 1  # 사용 중
    INACTIVE = 2  # 대기 중

    # RENT STATUS ID
    IN_PROGRESS = 1  # 진행 중
    CANCELED = 3  # 취소됨
    COMPLETED = 4  # 완료됨

    # USAGE STATUS ID
    IN_USE = 1  # 사용 중
    COMPLETED = 2  # 완료됨
    
    @staticmethod
    def get_options_for_rent(
        session: Session,
        selected_option_types: List[SelectedOptionType]
    ) -> List[Option]:
        """렌트에 필요한 옵션 조회"""
        selected_options = []
    
        for opt_type in selected_option_types:
            # 각 옵션 타입별로 필요한 수량만큼 조회
            options = option_crud.get_available_options_by_type(
                session=session,
                option_type_id=opt_type.optionTypeId,
                required_quantity=opt_type.quantity,
                status_id=RentService.INACTIVE
            )
            selected_options.extend(options)
            
        return selected_options

    @staticmethod
    def create_rent_history(rent_request: RentRequest, user_pk: int, options_count: int) -> RentHistory:
        """렌트 기록 생성"""
        return RentHistory(
            user_pk=user_pk,
            departure_location=f"({rent_request.autonomousDeparturePoint.x}, {rent_request.autonomousDeparturePoint.y})",
            arrival_location=f"({rent_request.autonomousArrivalPoint.x}, {rent_request.autonomousArrivalPoint.y})",
            cost=500 + (options_count * 50),
            mileage=0,
            status_id=RentService.IN_PROGRESS,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @staticmethod
    def create_usage_entries(
        rent_id: int,
        vehicle_id: int,
        module_id: int,
        selected_options: List[int]
    ) -> List[UsageHistory]:
        """사용 기록 엔트리 생성"""
        return [
            # 차량 사용 기록
            UsageHistory(
                rent_id=rent_id,
                item_id=vehicle_id,
                item_type_id=RentService.VEHICLE,
                status_id=RentService.IN_USE
            ),
            # 모듈 사용 기록
            UsageHistory(
                rent_id=rent_id,
                item_id=module_id,
                item_type_id=RentService.MODULE,
                status_id=RentService.IN_USE
            ),
            # 옵션 사용 기록
            *[
                UsageHistory(
                    rent_id=rent_id,
                    item_id=option_id,
                    item_type_id=RentService.OPTION,
                    status_id=RentService.IN_USE
                )
                for option_id in selected_options
            ]
        ]

    @staticmethod
    @handle_transaction
    def create_rent(
        session: Session, 
        rent_request: RentRequest, 
        user_pk: int
    ) -> RentResponse:
        """렌트 생성"""

        # 2. 사용 가능한 차량/모듈 조회
        vehicle = vehicle_crud.get_first_vehicle_by_status_id(
            session, 
            status_id=RentService.INACTIVE
        )
        
        module = module_crud.get_first_module_by_status_id(
            session, 
            status_id=RentService.INACTIVE
        )

        # 3. 선택된 옵션 조회
        selected_options = RentService.get_options_for_rent(
            session, 
            rent_request.selectedOptionTypes
        )

        # 4. 렌트 기록 생성
        rent_history = RentService.create_rent_history(
            rent_request, 
            user_pk, 
            len(selected_options)
        )
        rent_history = rent_history_crud.create(session, rent_history)
        session.refresh(rent_history)

        # 5. 사용 상태 업데이트
        vehicle_crud.update(
            session, 
            vehicle.vehicle_id, 
            {"status_id": RentService.ACTIVE}
        )
        module_crud.update(
            session, 
            module.module_id, 
            {"status_id": RentService.ACTIVE}
        )
        for option in selected_options:
            option_crud.update(
                session,
                option.option_id,
                {"status_id": RentService.ACTIVE}
            )

        # 6. 사용 기록 생성
        usage_entries = RentService.create_usage_entries(
            rent_history.rent_id,
            vehicle.vehicle_id,
            module.module_id,
            [opt.option_id for opt in selected_options]
        )
        for entry in usage_entries:
            session.add(entry)

        return RentResponse(
            rent_id=rent_history.rent_id,
            vehicle_number=vehicle.vehicle_number
        )

    @staticmethod
    @handle_transaction
    def cancel_rent(
        session: Session, 
        cancel_rent_req: CancelRentRequest, 
        user_pk: int
    ) -> CancelRentResponse:
        """렌트 취소 처리"""

        # 1. 렌트 기록 조회 및 검증
        rent_history = rent_history_crud.get_by_id(
            session, 
            cancel_rent_req.rent_id
        )
        
        if not rent_history:
            raise NotFoundError(
                message="Rent history not found",
                detail={
                    "rent_id": cancel_rent_req.rent_id
                }
            )

        # 2. 렌트 상태 검증
        if rent_history.status_id in [RentService.CANCELED, RentService.COMPLETED]:
            raise ValidationError(
                message="Rent already canceled or completed",
                detail={
                    "rent_id": cancel_rent_req.rent_id,
                    "current_status": rent_history.status_id
                }
            )

        # 3. 사용자 권한 검증
        if rent_history.user_pk != user_pk:
            raise ValidationError(
                message="Unauthorized rent access",
                detail={
                    "rent_id": cancel_rent_req.rent_id,
                    "request_user": user_pk,
                    "rent_user": rent_history.user_pk
                }
            )

        # 2. 사용 기록 조회
        usage_entries = usage_history_crud.get_usage_entries(
            session,
            cancel_rent_req.rent_id
        )

        # 3. 아이템 ID 분류
        vehicle_id = next(
            (u.item_id for u in usage_entries if u.item_type_id == RentService.VEHICLE),
            None
        )
        module_id = next(
            (u.item_id for u in usage_entries if u.item_type_id == RentService.MODULE),
            None
        )
        option_ids = [
            u.item_id for u in usage_entries 
            if u.item_type_id == RentService.OPTION
        ]

        # 4. 사용 기록 및 아이템 상태 업데이트
        usage_history_crud.cancel_usage_entries(
            session,
            cancel_rent_req.rent_id,
            vehicle_id,
            module_id,
            option_ids
        )
        
        # 5. 렌트 상태 업데이트
        rent_history_crud.update(
            session,
            cancel_rent_req.rent_id,
            {"status_id": RentService.CANCELED}
        )
        
        return CancelRentResponse(
            rent_id=cancel_rent_req.rent_id,
            message="Rent successfully canceled"
        )