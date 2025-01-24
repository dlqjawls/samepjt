from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime
from app.models.vehicle import Vehicle
from app.models.module import Module
from app.models.option import Option
from app.models.rent_history import RentHistory
from app.api.schemas.user.rent import RentRequest
from app.models.enum import ItemStatus

def get_available_vehicle(session: Session) -> Vehicle:
    """ 사용 가능한 차량 조회 """
    statement = select(Vehicle).where(Vehicle.status == ItemStatus.INACTIVE).limit(1)
    vehicle = session.exec(statement).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="No available vehicle found")
    return vehicle

def get_available_module(session: Session) -> Module:
    """ 사용 가능한 모듈 조회 """
    statement = select(Module).where(Module.status == ItemStatus.INACTIVE).limit(1)
    module = session.exec(statement).first()
    if not module:
        raise HTTPException(status_code=404, detail="No available module found")
    return module

def get_available_options(session: Session, selected_option_types: list) -> list[Option]:
    """ 사용 가능한 옵션 목록 조회 """
    selected_options: list[Option] = []
    for opt in selected_option_types:
        statement = select(Option).where(
            Option.optionType == opt.optionTypeId,
            Option.status == ItemStatus.INACTIVE
        ).limit(opt.quantity)
        options = session.exec(statement).all()

        if len(options) < opt.quantity:
            raise HTTPException(status_code=404, detail=f"Not enough options available for type {opt.optionTypeId}")

        selected_options.extend(options)

    return selected_options

def create_rent(session: Session, rent_request: RentRequest, user_pk: int) -> dict:
    """ 렌트 기록 생성 """
    vehicle = get_available_vehicle(session)
    module = get_available_module(session)
    selected_options = get_available_options(session, rent_request.selectedOptionTypes)

    rent_history = RentHistory(
        userPK=user_pk,
        departureLocation=f"({rent_request.autonomousDeparturePoint.x}, {rent_request.autonomousDeparturePoint.y})",
        arrivalLocation=f"({rent_request.autonomousArrivalPoint.x}, {rent_request.autonomousArrivalPoint.y})",
        rentStatus="IN_PROGRESS",
        startTime=rent_request.rentStartDate,
        endTime=rent_request.rentEndDate,
        baseCost=500,  # 기본 요금 (예제 값)
        additionalCost=len(selected_options) * 50,  # 옵션당 추가 비용
        totalCost=500 + (len(selected_options) * 50),
        statusUpdatedAt=datetime.now(),
    )

    session.add(rent_history)
    session.commit()
    session.refresh(rent_history)
    # 차량 및 모듈 상태 업데이트
    vehicle.status = ItemStatus.ACTIVE
    module.status = ItemStatus.ACTIVE
    for option in selected_options:
        option.status = ItemStatus.ACTIVE

    session.commit()

    return {
        "rent_id": rent_history.rentId,
        "vehicle_number": vehicle.vehicleNumber,
    }
