from datetime import datetime, timedelta
from typing import List
from sqlmodel import Session
from app.db.models.option import Option
from app.db.models.rent_history import RentHistory
from app.api.schemas.user import rent_schema
from app.utils.exceptions import ConflictError, ForbiddenError, NotFoundError, DatabaseError
from app.utils.handle_transaction import handle_transaction
from app.db.crud.rent_history import rent_history_crud
from app.db.crud.vehicle import vehicle_crud
from app.db.crud.module import module_crud
from app.db.crud.option import option_crud
from app.db.crud.usage_history import usage_history_crud
from app.utils.lut_constants import ItemType, ItemStatus, RentStatus, UsageStatus
import json


class RentService:
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
                status_id=ItemStatus.INACTIVE
            )
        ]

    @staticmethod
    def create_rent_history(rent_request: rent_schema.RentRequest, user_pk: int, options_count: int) -> RentHistory:
        """렌트 기록 생성"""
        return RentHistory(
            user_pk=user_pk,
            departure_location=json.dumps({
                "x": rent_request.autonomousDeparturePoint.x,
                "y": rent_request.autonomousDeparturePoint.y,
            }),
            arrival_location=json.dumps({
                "x": rent_request.autonomousArrivalPoint.x,
                "y": rent_request.autonomousArrivalPoint.y,
            }),
            cost=500 + (options_count * 50),
            mileage=0,
            status_id=RentStatus.IN_PROGRESS,
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

        if rent_history.rent_id is None:
            raise DatabaseError(
                message="Missing rent history ID after creation",
                detail={"rent_history": rent_history.dict()}
            )
        if vehicle.vehicle_id is None:
            raise DatabaseError(
                message="Missing vehicle ID",
                detail={"vehicle": vehicle.dict()}
            )
        if module.module_id is None:
            raise DatabaseError(
                message="Missing module ID",
                detail={"module": module.dict()}
            )

        # 5. 사용 상태 업데이트
        vehicle_crud.update(
            session, 
            vehicle.vehicle_id, 
            {"status_id": ItemStatus.ACTIVE},
            id_field="vehicle_id"
        )
        module_crud.update(
            session, 
            module.module_id, 
            {"status_id": ItemStatus.ACTIVE},
            id_field="module_id"
        )

        for option in selected_options:
            option_crud.update(
                session,
                option.option_id,
                {"status_id": ItemStatus.ACTIVE},
                id_field="option_id"
            )

        # 6. 사용 기록 생성
        option_ids = []
        for opt in selected_options:
            if opt.option_id is None:
                raise DatabaseError(
                    message="Missing option ID",
                    detail={"option": opt.dict()}
                )
            option_ids.append(opt.option_id)

        usage_entries = usage_history_crud.create_usage_entries(
            session=session,
            rent_id=rent_history.rent_id,
            vehicle_id=vehicle.vehicle_id,
            module_id=module.module_id,
            option_ids=option_ids
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
        # 3. 렌트 상태 검증
        if rent_history.status_id in [RentStatus.CANCELED, RentStatus.COMPLETED]:
            raise ConflictError(
                message="Rent already canceled or completed",
                detail={
                    "rent_id": rent_id,
                    "current_status": rent_history.status_id
                }
            )

     
        # 4. 사용 기록 조회
        usage_entries = usage_history_crud.get_usage_entries(
            session,
            rent_id
        )
        # 5. 아이템 ID 분류
        vehicle_id = next(
            (u.item_id for u in usage_entries if u.item_type_id == ItemType.VEHICLE),
            None
        )
        module_id = next(
            (u.item_id for u in usage_entries if u.item_type_id == ItemType.MODULE),
            None
        )
        option_ids = [
            u.item_id for u in usage_entries 
            if u.item_type_id == ItemType.OPTION
        ]
        
        # 6. 사용 기록 업데이트트
        usage_history_crud.update_usage_entries_status(
            session,
            rent_id,
            vehicle_id,
            module_id,
            option_ids,
            UsageStatus.COMPLETED
        )
        
        # 아이템 상태 업데이트
        vehicle_crud.update(
            session,
            vehicle_id,
            {"status_id": ItemStatus.INACTIVE},
            id_field="vehicle_id"
        )
        module_crud.update(
            session,
            module_id,
            {"status_id": ItemStatus.INACTIVE},
            id_field="module_id"
        )

        for option_id in option_ids:
            option_crud.update(
                session,
                option_id,
                {"status_id": ItemStatus.INACTIVE},
                id_field="option_id"
            )   
        # 7. 렌트 상태 업데이트
        rent_history_crud.update(
            session,
            rent_id,
            obj_in={"status_id": RentStatus.CANCELED},
            id_field="rent_id"
        )
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
        if rent_history.status_id in [RentStatus.CANCELED, RentStatus.COMPLETED]:
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

    @staticmethod
    @handle_transaction
    def complete_rent(
        session: Session,
        rent_id: int,
        user_pk: int
    ) -> rent_schema.CompleteRentResponse:
        """렌트 완료 처리"""
        
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
        if rent_history.status_id in [RentStatus.CANCELED, RentStatus.COMPLETED]:
            raise ConflictError(
                message="Rent already completed or canceled",
                detail={
                    "rent_id": rent_id,
                    "current_status": rent_history.status_id
                }
            )

        # 4. 사용 기록 조회
        usage_entries = usage_history_crud.get_usage_entries(session, rent_id)

        # 5. 아이템 ID 분류
        vehicle_id = next(
            (u.item_id for u in usage_entries if u.item_type_id == ItemType.VEHICLE),
            None
        )
        module_id = next(
            (u.item_id for u in usage_entries if u.item_type_id == ItemType.MODULE),
            None
        )
        option_ids = [
            u.item_id for u in usage_entries 
            if u.item_type_id == ItemType.OPTION
        ]

        # 6. 사용 기록 및 아이템 상태 업데이트
        usage_history_crud.update_usage_entries_status(
            session,
            rent_id,
            vehicle_id,
            module_id,
            option_ids,
            UsageStatus.COMPLETED
        )       # 아이템 상태 업데이트
        vehicle_crud.update(
            session,
            vehicle_id,
            {"status_id": ItemStatus.INACTIVE},
            id_field="vehicle_id"
        )
        module_crud.update(
            session,
            module_id,
            {"status_id": ItemStatus.INACTIVE},
            id_field="module_id"
        )

        for option_id in option_ids:
            option_crud.update(
                session,
                option_id,
                {"status_id": ItemStatus.INACTIVE},
                id_field="option_id"
            )   

        # 7. 렌트 상태 업데이트 및 최종 데이터 계산
        usage_duration = int((datetime.now() - rent_history.created_at).total_seconds() / 60)
        total_mileage = 150.0  # TODO: 실제 주행거리 계산 로직 구현
        estimated_payback = rent_history.cost * 0.05  # TODO: 실제 페이백 계산 로직 구현

        rent_history_crud.update(
            session,
            rent_id,
            obj_in={
                "status_id": RentStatus.COMPLETED,
                "mileage": total_mileage,
                "updated_at": datetime.now()
            },
            id_field="rent_id"
        )

        return rent_schema.CompleteRentResponse(
            message="Rental completed successfully",
            data=rent_schema.CompleteRentResponseData(
                rent_id=rent_id,
                total_mileage=total_mileage,
                usage_duration=usage_duration,
                estimated_payback_amount=estimated_payback
            )
        )