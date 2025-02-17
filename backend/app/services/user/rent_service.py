from datetime import datetime, timedelta
from typing import List, Tuple
import json
import math
from sqlmodel import Session

from app.db.models.option import Option
from app.db.models.rent_history import RentHistory
from app.api.schemas.user import rent_schema
from app.utils.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError, DatabaseError
from app.utils.handle_transaction import handle_transaction
from app.db.crud.rent_history import rent_history_crud
from app.db.crud.vehicle import vehicle_crud
from app.db.crud.module import module_crud
from app.db.crud.option import option_crud
from app.db.crud.usage_history import usage_history_crud
from app.utils.lut_constants import ItemType, ItemStatus, RentStatus, UsageStatus
from app.db.crud.lut import module_type as module_type_crud
from app.db.crud.option_type import option_type_crud
from app.core.redis import redis_handler
from app.websocket.websocket import WebSocketService

class RentService:
    # 최소 대여 시간
    MIN_HOURS = 6
    # 시간 당 이용료
    HOURLY_RATE = 10000
  
    @staticmethod
    def calculate_rental_cost(rent_start: datetime, rent_end: datetime) -> int:
        total_seconds = (rent_end - rent_start).total_seconds()
        total_hours = total_seconds / 3600

        # 최소 대여 시간 적용
        billable_hours = max(total_hours, RentService.MIN_HOURS)
        cost = math.ceil(billable_hours) * RentService.HOURLY_RATE
        
        return int(cost)

    @staticmethod
    def get_options_for_rent(
        session: Session,
        selected_option_types: List[rent_schema.SelectedOptionType]
    ) -> List[Option]:
        """선택된 옵션 타입에 따른 렌트 옵션을 조회합니다."""
        return [
            option
            for opt_type in selected_option_types
            for option in option_crud.get_available_options_by_type(
                session=session,
                option_type_id=opt_type.optionTypeId,
                required_quantity=opt_type.quantity,
                item_status_id=ItemStatus.INACTIVE.ID
            )
        ]

    @staticmethod
    def create_rent_history(
        rent_request: rent_schema.RentRequest,
        user_pk: int,
        options_count: int
    ) -> RentHistory:
        """새로운 렌트 기록을 생성합니다."""
        departure = {
            "x": rent_request.autonomousDeparturePoint.x,
            "y": rent_request.autonomousDeparturePoint.y,
        }
        arrival = {
            "x": rent_request.autonomousArrivalPoint.x,
            "y": rent_request.autonomousArrivalPoint.y,
        }
        cost = rent_request.cost
        now = datetime.now()
        return RentHistory(
            user_pk=user_pk,
            departure_location=json.dumps(departure),
            arrival_location=json.dumps(arrival),
            cost=cost,
            mileage=0,
            rent_status_id=RentStatus.IN_PROGRESS.ID,
            rent_start_date=rent_request.rentStartDate,
            rent_end_date=rent_request.rentEndDate,
            created_at=now,
            updated_at=now
        )

    @staticmethod
    def _check_required_ids(rent_history: RentHistory, vehicle, module) -> None:
        """생성된 렌트 기록과 관련 아이템의 ID가 존재하는지 검증합니다."""
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

    @staticmethod
    def _activate_items(
        session: Session,
        vehicle,
        module,
        options: List[Option]
    ) -> None:
        """렌트 시작 시 아이템의 상태를 ACTIVE로 업데이트합니다."""
        vehicle_crud.update(
            session,
            vehicle.vehicle_id,
            {"item_status_id": ItemStatus.ACTIVE.ID},
            id_field="vehicle_id"
        )
        module_crud.update(
            session,
            module.module_id,
            {"item_status_id": ItemStatus.ACTIVE.ID},
            id_field="module_id"
        )
        for option in options:
            option_crud.update(
                session,
                option.option_id,
                {"item_status_id": ItemStatus.ACTIVE.ID},
                id_field="option_id"
            )

    @staticmethod
    def _deactivate_items(
        session: Session,
        vehicle_id: int,
        module_id: int,
        option_ids: List[int]
    ) -> None:
        """렌트 취소/완료 시 아이템의 상태를 INACTIVE로 업데이트합니다."""
        vehicle_crud.update(
            session,
            vehicle_id,
            {"item_status_id": ItemStatus.INACTIVE.ID},
            id_field="vehicle_id"
        )
        module_crud.update(
            session,
            module_id,
            {"item_status_id": ItemStatus.INACTIVE.ID},
            id_field="module_id"
        )
        for option_id in option_ids:
            option_crud.update(
                session,
                option_id,
                {"item_status_id": ItemStatus.INACTIVE.ID},
                id_field="option_id"
            )

    @staticmethod
    def _validate_rent_history(
        session: Session,
        rent_id: int,
        user_pk: int,
        check_status: bool = True
    ) -> RentHistory:
        """
        렌트 기록을 조회하고 사용자 권한 및 상태(취소/완료 여부)를 검증합니다.
        
        Args:
            session: DB 세션.
            rent_id: 렌트 기록 ID.
            user_pk: 사용자 PK.
            check_status: True인 경우, 렌트가 이미 취소되었거나 완료되었으면 오류를 발생합니다.
            
        Returns:
            RentHistory 객체.
            
        Raises:
            NotFoundError, ForbiddenError, ConflictError
        """
        rent_history = rent_history_crud.get_by_id(session, rent_id)
        if not rent_history:
            raise NotFoundError(
                message="Rent history not found",
                detail={"rent_id": rent_id}
            )
        if rent_history.user_pk != user_pk:
            raise ForbiddenError(
                message="Permission denied",
                detail={
                    "rent_id": rent_id,
                    "request_user": user_pk,
                    "rent_user": rent_history.user_pk
                }
            )
        if check_status and rent_history.rent_status_id in [RentStatus.CANCELED.ID, RentStatus.COMPLETED.ID]:
            raise ConflictError(
                message="rent already completed or canceled",
                detail={
                    "rent_id": rent_id,
                    "current_status": rent_history.rent_status_id
                }
            )
        return rent_history

    @staticmethod
    def _extract_usage_ids(usage_entries) -> Tuple[int, int, List[int]]:
        """
        사용 기록에서 차량, 모듈, 옵션의 ID를 추출합니다.
        
        Returns:
            (vehicle_id, module_id, option_ids)
        """
        vehicle_id = next(
            (entry.item_id for entry in usage_entries if entry.item_type_id == ItemType.VEHICLE.ID),
            None
        )
        module_id = next(
            (entry.item_id for entry in usage_entries if entry.item_type_id == ItemType.MODULE.ID),
            None
        )
        option_ids = [
            entry.item_id for entry in usage_entries if entry.item_type_id == ItemType.OPTION.ID  
        ]
        if vehicle_id is None:
            raise DatabaseError(
                message="Missing vehicle ID",
                detail={"vehicle_id": vehicle_id}
            )
        if module_id is None:
            raise DatabaseError(
                message="Missing module ID",
                detail={"module_id": module_id}
            )
        
        return vehicle_id, module_id, option_ids

    @staticmethod
    @handle_transaction
    def create_rent(
        session: Session, 
        rent_request: rent_schema.RentRequest, 
        user_pk: int
    ) -> rent_schema.RentResponse:
        """새로운 렌트 프로세스를 생성합니다."""
        # 차량 및 모듈 가용성 검증
        vehicle = vehicle_crud.get_first_available_vehicle(session)
        module = module_crud.get_first_available_module(session)
        
        # 차량 연결 상태 검증
        vehicle_key = f"vehicle:{vehicle.vin}"
        vehicle_status = redis_handler.get(vehicle_key)
        if vehicle_status != "connected":
            raise ConflictError(message="차량이 네트워크에 연결되지 않았습니다.")
        
        # 2. 선택된 옵션들을 검증 및 조회
        selected_options : List[Option] = []
        for opt_type in rent_request.selectedOptionTypes:
            options = option_crud.get_available_options_by_type(
                session=session,
                option_type_id=opt_type.optionTypeId,
                required_quantity=opt_type.quantity
            )
            selected_options.extend(options)

        # 3. 가격 검증
        module_type_cost = module_type_crud.get_by_id(session, rent_request.moduleTypeId).module_type_cost
        option_cost = sum(option_type_crud.get_option_cost_by_id(session, option.option_type_id) for option in selected_options)
        date_cost = RentService.calculate_rental_cost(rent_request.rentStartDate, rent_request.rentEndDate)
        
        # 총 비용 검증
        total_cost = module_type_cost + option_cost + date_cost
        if rent_request.cost != total_cost:
            raise BadRequestError(
                message="Invalid cost",
                detail={
                    "module_type_cost": module_type_cost,
                    "option_cost": option_cost,
                    "date_cost": date_cost,
                    "total_cost": total_cost
                }
            )

        # 3. 렌트 기록 생성
        rent_history = rent_history_crud.create(
            session,
            RentService.create_rent_history(rent_request, user_pk, len(selected_options))
        )
        session.refresh(rent_history)
        RentService._check_required_ids(rent_history, vehicle, module)

        # 4. 아이템 상태 업데이트 (ACTIVE)
        RentService._activate_items(session, vehicle, module, selected_options)

        # 5. 사용 기록 생성
        option_ids = [option.option_id for option in selected_options if option.option_id is not None]
        if len(option_ids) != len(selected_options):
            missing_options = [option.dict() for option in selected_options if option.option_id is None]
            raise DatabaseError(
                message="Missing option ID(s)",
                detail={"options": missing_options}
            )
        if rent_history.rent_id is None:
            raise DatabaseError(
                message="Missing rent history ID",
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

        usage_history_crud.create_usage_entries(
            session=session,
            rent_id=rent_history.rent_id,
            vehicle_id=vehicle.vehicle_id,
            module_id=module.module_id,
            option_ids=option_ids
        )
        
        WebSocketService.trigger_send_rent_request_message(vehicle.vin, rent_history.rent_id, module.module_nfc_tag_id)
        
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
        """진행 중인 렌트를 취소합니다."""
        # 1. 렌트 기록 및 사용자 권한 검증
        rent_history = RentService._validate_rent_history(session, rent_id, user_pk)
        
        # 2. 사용 기록에서 아이템 ID 추출
        usage_entries = usage_history_crud.get_usage_entries(session, rent_id)
        vehicle_id, module_id, option_ids = RentService._extract_usage_ids(usage_entries)

        # 3. 사용 기록 및 아이템 상태 업데이트 (비활성화)
        usage_history_crud.update_usage_entries_status(
            session,
            rent_id,
            vehicle_id,
            module_id,
            option_ids,
            UsageStatus.COMPLETED.ID
        )
        RentService._deactivate_items(session, vehicle_id, module_id, option_ids)

        # 4. 렌트 상태 업데이트 (CANCELED)
        rent_history_crud.update(
            session,
            rent_id,
            obj_in={"rent_status_id": RentStatus.CANCELED.ID},
            id_field="rent_id"
        )
        
        vehicle = vehicle_crud.get_by_id(session, vehicle_id)
        module = module_crud.get_by_id(session, module_id)
        WebSocketService.trigger_send_return_message(vehicle.vin, rent_id, module.module_nfc_tag_id)
        
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
        """진행 중인 렌트의 상태 정보를 조회합니다."""
        # 렌트 기록 및 사용자 권한 검증
        rent_history = RentService._validate_rent_history(session, rent_id, user_pk)
        
        # 예시를 위한 더미 데이터 구성
        current_location = rent_schema.Coordinate(x=12.3123, y=32.3232)
        dest_location = rent_schema.Coordinate(x=12.313, y=32.3232)
        
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
        """진행 중인 렌트를 완료합니다."""
        # 1. 렌트 기록 및 사용자 권한 검증
        rent_history = RentService._validate_rent_history(session, rent_id, user_pk)
        
        # 2. 사용 기록에서 아이템 ID 추출
        usage_entries = usage_history_crud.get_usage_entries(session, rent_id)
        vehicle_id, module_id, option_ids = RentService._extract_usage_ids(usage_entries)

        # 3. 사용 기록 및 아이템 상태 업데이트 (비활성화)
        usage_history_crud.update_usage_entries_status(
            session,
            rent_id,
            vehicle_id,
            module_id,
            option_ids,
            UsageStatus.COMPLETED.ID
        )
        RentService._deactivate_items(session, vehicle_id, module_id, option_ids)

        # 4. 사용 기간, 주행 거리 및 페이백 계산
        usage_duration = int((datetime.now() - rent_history.created_at).total_seconds() / 60)
        total_mileage = 150.0  # TODO: 실제 주행 거리 계산 로직 구현
        estimated_payback = rent_history.cost * 0.05  # TODO: 실제 페이백 계산 로직 구현

        # 5. 렌트 기록 업데이트 (COMPLETED)
        rent_history_crud.update(
            session,
            rent_id,
            obj_in={
                "rent_status_id": RentStatus.COMPLETED.ID,
                "mileage": total_mileage,
                "updated_at": datetime.now()
            },
            id_field="rent_id"
        )
        
        vehicle = vehicle_crud.get_by_id(session, vehicle_id)
        module = module_crud.get_by_id(session, module_id)
        WebSocketService.trigger_send_return_message(vehicle.vin, rent_id, module.module_nfc_tag_id)
        
        return rent_schema.CompleteRentResponse(
            message="Rental completed successfully",
            data=rent_schema.CompleteRentResponseData(
                rent_id=rent_id,
                total_mileage=total_mileage,
                usage_duration=usage_duration,
                estimated_payback_amount=estimated_payback
            )
        )
