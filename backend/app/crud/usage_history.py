from sqlmodel import Session, select, update
from app.models.vehicle import Vehicle
from app.models.module import Module
from app.models.option import Option
from app.models.usage_history import UsageHistory
from app.crud.base import CRUDBase
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Any, Dict, List

from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError

class UsageHistoryCRUD(CRUDBase[UsageHistory]):
    def __init__(self):
        super().__init__(UsageHistory, "usage_id")
          
    def get_item_usage_history(
        self,
        session: Session,
        item_id: int,
        item_type_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """특정 아이템의 사용 기록 조회

        Args:
            session: DB 세션
            item_id: 아이템 ID
            item_type_id: 아이템 타입 ID (1: 차량, 2: 모듈, 3: 옵션)
            page: 페이지 번호 (기본값: 1)
            page_size: 페이지 크기 (기본값: 10)

        Returns:
            Dict[str, Any]: {
                "items": List[UsageHistory],
                "pagination": {...},
                "summary": {
                    "total_usages": int,
                    "current_status": str
                }
            }

        Raises:
            ValidationError: 잘못된 입력값
            NotFoundError: 사용 기록이 없는 경우
            DatabaseError: DB 조회 실패
        """
        try:
            # 1. 입력값 검증
            if item_id <= 0:
                raise ValidationError(
                    message="Invalid item ID",
                    detail={
                        "item_id": item_id,
                        "error": "Item ID must be positive"
                    }
                )

            if item_type_id not in [1, 2, 3]:  # VEHICLE, MODULE, OPTION
                raise ValidationError(
                    message="Invalid item type ID",
                    detail={
                        "item_type_id": item_type_id,
                        "error": "Item type ID must be 1(vehicle), 2(module), or 3(option)"
                    }
                )

            # 2. 사용 기록 조회
            query = (
                select(self.model)
                .where(
                    self.model.item_id == item_id,
                    self.model.item_type_id == item_type_id
                )
            )

            # 3. 페이지네이션 적용
            paginated_result = self.paginate(
                session=session,
                page=page,
                page_size=page_size,
                query=query
            )

            # 4. 결과 검증
            if not paginated_result["items"]:
                raise NotFoundError(
                    message="No usage history found",
                    detail={
                        "item_id": item_id,
                        "item_type_id": item_type_id
                    }
                )

            # 5. 현재 상태 조회를 위한 최신 기록
            latest_usage = paginated_result["items"][0]

            # 6. 응답 데이터 구성
            return {
                "items": paginated_result["items"],
                "pagination": paginated_result["pagination"],
                "summary": {
                    "total_usages": paginated_result["pagination"]["total_items"],
                    "current_status": "ACTIVE" if latest_usage.status_id == 1 else "INACTIVE"
                }
            }

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch item usage history",
                detail={
                    "error": str(e),
                    "item_id": item_id,
                    "item_type_id": item_type_id
                }
            )
      
    def get_usage_entries(
        self,
        session: Session,
        rent_id: int
    ) -> List[UsageHistory]:
        """렌트의 사용 기록 조회"""
        usage_entries = session.exec(
            select(UsageHistory)
            .where(UsageHistory.rent_id == rent_id)
        ).all()

        return list(usage_entries)

    def create_usage_entries(
        self,
        session: Session,
        rent_id: int,
        vehicle_id: int,
        module_id: int,
        option_ids: List[int]
    ) -> List[UsageHistory]:
        """렌트에 대한 사용 기록 생성
        
        Args:
            session: DB 세션
            rent_id: 렌트 ID
            vehicle_id: 차량 ID
            module_id: 모듈 ID
            option_ids: 옵션 ID 리스트

        Returns:
            List[UsageHistory]: 생성된 사용 기록 리스트

        Raises:
            ValidationError: 잘못된 입력값
            DatabaseError: DB 오류
        """
        try:
            # 1. 입력값 검증
            if rent_id <= 0:
                raise ValidationError(
                    message="Invalid rent ID",
                    detail={"rent_id": rent_id}
                )
            if vehicle_id <= 0:
                raise ValidationError(
                    message="Invalid vehicle ID",
                    detail={"vehicle_id": vehicle_id}
                )
            if module_id <= 0:
                raise ValidationError(
                    message="Invalid module ID",
                    detail={"module_id": module_id}
                )
            if any(opt_id <= 0 for opt_id in option_ids):
                raise ValidationError(
                    message="Invalid option ID",
                    detail={"option_ids": option_ids}
                )

            # 2. 사용 기록 생성
            usage_entries = []

            # 2.1 차량 사용 기록
            vehicle_usage = UsageHistory(
                rent_id=rent_id,
                item_id=vehicle_id,
                item_type_id=1,  # VEHICLE
                status_id=1      # ACTIVE
            )
            usage_entries.append(vehicle_usage)

            # 2.2 모듈 사용 기록
            module_usage = UsageHistory(
                rent_id=rent_id,
                item_id=module_id,
                item_type_id=2,  # MODULE
                status_id=1      # ACTIVE
            )
            usage_entries.append(module_usage)

            # 2.3 옵션 사용 기록
            for option_id in option_ids:
                option_usage = UsageHistory(
                    rent_id=rent_id,
                    item_id=option_id,
                    item_type_id=3,  # OPTION
                    status_id=1      # ACTIVE
                )
                usage_entries.append(option_usage)

            # 3. DB에 저장
            for entry in usage_entries:
                session.add(entry)
            session.flush()

            return usage_entries

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to create usage entries",
                detail={
                    "error": str(e),
                    "rent_id": rent_id
                }
            )
    
    def cancel_usage_entries(
        self,
        session: Session,
        rent_id: int,
        vehicle_id: int,
        module_id:int,
        option_ids: List[int]
    ) -> None:
        """사용 기록 및 아이템 상태 업데이트"""
        # 사용 기록 상태 업데이트
        session.execute(
            update(UsageHistory)
            .where(UsageHistory.rent_id == rent_id)
            .values(status_id=2)  # INACTIVE
        )

        # 차량 상태 업데이트
        if vehicle_id:
            session.execute(
                update(Vehicle)
                .where(Vehicle.vehicle_id == vehicle_id)
                .values(status_id=2)  # INACTIVE
            )

        # 모듈 상태 업데이트
        if module_id:
            session.execute(
                update(Module)
                .where(Module.module_id == module_id)
                .values(status_id=2)  # INACTIVE
            )

        # 옵션 상태 업데이트
        if option_ids:
            session.execute(
                update(Option)
                .where(Option.option_id.in_(option_ids))
                .values(status_id=2)  # INACTIVE
            )

usage_history_crud = UsageHistoryCRUD()
