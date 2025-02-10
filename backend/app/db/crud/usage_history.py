from sqlmodel import Session, select, update
from app.db.models.usage_history import UsageHistory
from app.db.crud.base import CRUDBase
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, List, Optional
from app.utils.lut_constants import ItemType, UsageStatus
from app.utils.exceptions import DatabaseError, ValidationError

class UsageHistoryCRUD(CRUDBase[UsageHistory]):

    def __init__(self):
        super().__init__(UsageHistory)
          
    
    def _update_status(
        self,
        session: Session,
        model,
        identifier: int,
        field_name: str,
        item_status_id: int,
        extra_conditions: Optional[List[Any]] = None

    ) -> None:
        """지정된 모델의 특정 필드를 기준으로 상태 업데이트를 수행하는 헬퍼 메서드입니다.
        추가 조건이 있다면 rent id 등도 함께 필터링합니다.

      Args:
          session (Session): DB 세션
          model (_type_): 업데이트할 모델 (예: Vehicle, Module 등)
          identifier (int): 업데이트 대상의 ID
          field_name (str): 모델의 ID 필드 이름 (예: "vehicle_id", "module_id")
          item_status_id (int): 변경할 상태 ID
          extra_conditions (Optional[List[Any]], optional): 추가 조건 (예: rent id 등). Defaults to None.
      """

        condition = getattr(model, field_name) == identifier
        if extra_conditions:
            for cond in extra_conditions:
                condition = condition & cond
        session.execute(
            update(model)
            .where(condition)
            .values(item_status_id=item_status_id)
        )
        

        
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
            }

        Raises:
            ValidationError: 잘못된 입력값
            NotFoundError: 사용 기록이 없는 경우
            DatabaseError: DB 조회 실패
        """
        # 1. 입력값 검증
        if item_id <= 0:
            raise ValidationError(
                message="Invalid item ID",
                detail={
                    "item_id": item_id,
                    "error": "Item ID must be positive"
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


        return paginated_result
      
    def get_usage_entries(
        self,
        session: Session,
        rent_id: int
    ) -> List[UsageHistory]:
        """렌트의 사용 기록 조회

        Args:
            session (Session): DB 세션
            rent_id (int): 렌트 ID

        Returns:
            List[UsageHistory]: 사용 기록 리스트
        """

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
            items = [(ItemType.VEHICLE, vehicle_id), (ItemType.MODULE, module_id)] + [(ItemType.OPTION, oid) for oid in option_ids]
            usage_entries = [
                UsageHistory(rent_id=rent_id, item_id=item, item_type_id=item_type, usage_status_id=UsageStatus.IN_USE)
                for item_type, item in items if item > 0
            ]


            # DB에 일괄 저장
            session.add_all(usage_entries)
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


    def update_usage_entries_status(
        self,
        session: Session,
        rent_id: int,
        vehicle_id: Optional[int],
        module_id: Optional[int],
        option_ids: List[int],
        usage_status_id: int
    ) -> None:
        """사용 기록 및 아이템 상태 업데이트


        Args:
            session: DB 세션
            rent_id: 렌트 ID
            vehicle_id: 차량 ID
            module_id: 모듈 ID
            option_ids: 옵션 ID 목록
            usage_status_id: 변경할 상태 ID
        """
        try:

            # 업데이트 대상 및 항목 타입 매핑 (항목 타입: 1=차량, 2=모듈, 3=옵션)
            updates = []
            if vehicle_id is not None:
                updates.append((ItemType.VEHICLE, vehicle_id))
            if module_id is not None:
                updates.append((ItemType.MODULE, module_id))
            if option_ids:
                for oid in option_ids:
                    updates.append((ItemType.OPTION, oid))

            for item_type, item_id in updates:
                self._update_status(
                    session,
                    UsageHistory,
                    item_id,
                    "item_id",
                    usage_status_id,
                    extra_conditions=[UsageHistory.item_type_id == item_type, UsageHistory.rent_id == rent_id]

                )
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to update usage entries status",
                detail={
                    "error": str(e),
                    "rent_id": rent_id,
                    "usage_status_id": usage_status_id
                }
            )


usage_history_crud = UsageHistoryCRUD()
