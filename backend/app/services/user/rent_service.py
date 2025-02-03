from datetime import datetime, timedelta
from typing import List
from sqlmodel import Session
from app.models.option import Option
from app.models.rent_history import RentHistory
from app.api.schemas.user import rent_schema
from app.utils.exceptions import ConflictError, ForbiddenError, NotFoundError
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
        selected_option_types: List[rent_schema.SelectedOptionType]
    ) -> List[Option]:
        """렌트에 필요한 옵션 조회"""
        return [
            option
            for opt_type in selected_option_types
            for option in option_crud.get_available_options_by_type(
                session=session,
                option_type_id=opt_type.optionTypeId,  
                required_quantity=opt_type.quantity,
                status_id=RentService.INACTIVE
            )
        ]

    @staticmethod
    def create_rent_history(rent_request: rent_schema.RentRequest, user_pk: int, options_count: int) -> RentHistory:
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
    @handle_transaction
    def create_rent(
        session: Session, 
        rent_request: rent_schema.RentRequest, 
        user_pk: int
    ) -> rent_schema.RentResponse:
        """렌트 생성"""
        
        # 1. 차량 상태 검증
        vehicle = vehicle_crud.get_first_available_vehicle(session)

        # 2. 모듈 상태 검증 
        module = module_crud.get_first_available_module(session)

        # 3. 옵션 검증
        selected_options = []
        for opt_type in rent_request.selectedOptionTypes:
            options = option_crud.get_available_options_by_type(
                session=session,
                option_type_id=opt_type.optionTypeId,
                required_quantity=opt_type.quantity
            )
            selected_options.extend(options)


        # 4. 렌트 기록 생성
        rent_history = rent_history_crud.create(
            session,
            RentService.create_rent_history(rent_request, user_pk, len(selected_options))
        )
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
        usage_entries = usage_history_crud.create_usage_entries(
            session=session,
            rent_id=rent_history.rent_id,
            vehicle_id=vehicle.vehicle_id,
            module_id=module.module_id,
            option_ids=[opt.option_id for opt in selected_options]
        )

        return rent_schema.RentResponse(
          data=rent_schema.RentResponseData(
                rent_id=rent_history.rent_id,
                vehicle_number=vehicle.vehicle_number
            )
        )

    @staticmethod
    @handle_transaction
    def cancel_rent(
        session: Session, 
        rent_id: int, 
        user_pk: int
    ) -> rent_schema.CancelRentResponse:
        """렌트 취소 처리"""
        print( "렌트 취소 처리")
        # 1. 렌트 기록 조회 및 검증
        rent_history = rent_history_crud.get_by_id(
            session, 
            rent_id
        )
        if not rent_history:
            raise NotFoundError(
                message="Rent history not found",
                detail={
                    "rent_id": rent_id
                }
            )
        print( "렌트 기록 조회 및 검증")
        # 2. 사용자 권한 검증
        if rent_history.user_pk != user_pk:
            raise ForbiddenError(
                message="Unauthorized rent access",
                detail={
                    "rent_id": rent_id,
                    "request_user": user_pk,
                    "rent_user": rent_history.user_pk
                }
            )
        print( "사용자 권한 검증")
        # 3. 렌트 상태 검증
        if rent_history.status_id in [RentService.CANCELED, RentService.COMPLETED]:
            raise ConflictError(
                message="Rent already canceled or completed",
                detail={
                    "rent_id": rent_id,
                    "current_status": rent_history.status_id
                }
            )

     
        print( "렌트 상태 검증")
        # 4. 사용 기록 조회
        usage_entries = usage_history_crud.get_usage_entries(
            session,
            rent_id
        )
        print( "사용 기록 조회")
        # 5. 아이템 ID 분류
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
        print( "아이템 ID 분류")
        # 6. 사용 기록 및 아이템 상태 업데이트
        usage_history_crud.cancel_usage_entries(
            session,
            rent_id,
            vehicle_id,
            module_id,
            option_ids
        )
        print( "사용 기록 및 아이템 상태 업데이트")
        # 7. 렌트 상태 업데이트
        rent_history_crud.update(
            session=session,
            id=rent_id,
            obj_in={"status_id": RentService.CANCELED}
        )
        print( "렌트 상태 업데이트")
        return rent_schema.CancelRentResponse(
            message="Rent canceled successfully",
            data=rent_schema.CancelRentResponseData(
                rent_id=rent_id
            )
        )
        
    @staticmethod
    def get_rent_status(
        session: Session,
        rent_id: int,
        user_pk: int
    ) -> rent_schema.RentStatusResponse:
        """렌트 상태 조회
        
        Args:
            session: DB 세션
            rent_id: 렌트 ID
            user_pk: 사용자 PK
            
        Returns:
            렌트 상태 정보
            
        Raises:
            NotFoundError: 렌트 없음
            ForbiddenError: 권한 없음
            ConflictError: 이미 취소/완료됨
        """
        # 1. 렌트 기록 조회 및 검증
        rent_history = rent_history_crud.get_by_id(session, rent_id)
        if not rent_history:
            raise NotFoundError(
                message="Rent history not found",
                detail={"rent_id": rent_id}
            )

        # 2. 사용자 권한 검증
        if rent_history.user_pk != user_pk:
            raise ForbiddenError(
                message="Permission denied",
                detail={
                    "rent_id": rent_id,
                    "request_user": user_pk,
                    "rent_user": rent_history.user_pk
                }
            )

        # 3. 렌트 상태 검증
        if rent_history.status_id in [RentService.CANCELED, RentService.COMPLETED]:
            raise ConflictError(
                message="Rent already canceled or completed",
                detail={
                    "rent_id": rent_id,
                    "current_status": rent_history.status_id
                }
            )

        # 4. 더미 데이터로 상태 정보 생성
        current_location = rent_schema.Coordinate( x=12.3123, y=32.3232)
        dest_location = rent_schema.Coordinate (x=12.313, y=32.3232)
        
        return rent_schema.RentStatusResponse(
            message="Vehicle rent status retrieved successfully",
            data=rent_schema.RentStatusResponseData(
                isArrive=False,
                location=current_location,
                destination=dest_location,
                ETA=datetime.now() + timedelta(hours=1),
                distanceTravelled=120.0,
                plannedPath=[
                    current_location,
                    rent_schema.Coordinate(x=12.313, y=32.3232),
                    rent_schema.Coordinate(x=12.313, y=32.3232),
                    dest_location
                ],
                SLAMMapData="base64-encoded-map-data",
                status=rent_schema.RentStatus(
                    vehicle=rent_schema.VehicleStatus(
                        batteryLevel=50,
                        lightBrightness=60
                    ),
                    options=[
                        rent_schema.OptionStatus(optionName="Option 1", optionStatus="ACTIVE"),
                        rent_schema.OptionStatus(optionName="Option 2", optionStatus="ACTIVE")
                    ]
                )
            )
        )