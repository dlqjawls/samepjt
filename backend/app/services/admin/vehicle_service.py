from sqlmodel import Session
from app.api.schemas.admin.vehicle_shema import VehiclesData, VehiclesResponse
from app.crud.vehicle import vehicle_crud

class VehicleService:
    @staticmethod
    def get_vehicle_list(session: Session, page: int, page_size: int):
        """
        관리자 차량 목록 조회 서비스

        매개변수:
            session (Session): 데이터베이스 세션
            page (int): 조회할 페이지 번호 (최소 1)
            page_size (int): 한 페이지당 차량 개수 (최소 1)
        
        반환:
            VehiclesResponse: 차량 목록과 페이지네이션 정보를 포함한 응답 모델
        
        예외:
            DatabaseError: 차량 목록 조회에 실패한 경우
        """
        paginated_result = vehicle_crud.get_all(session, page, page_size)
        
        # vehicles_raw: ORM 객체 리스트를 가져옴
        vehicles_raw = paginated_result["items"]
        converted_vehicles = []
        # status 매핑 (필요에 따라 값 변경)
        status_mapping = {1: "Active", 2: "Inactive", 3: "Maintenance"}
        
        for vehicle in vehicles_raw:
            # ORM 객체를 dict로 변환
            vehicle_data = vehicle.dict()
            # current_location은 ORM에서는 문자열로 저장되어 있다고 가정 (예: "12.313,32.3232")
            try:
                parts = vehicle_data.get("current_location", "").split(",")
                if len(parts) >= 2:
                    current_location = {
                        "x": float(parts[0].strip()),
                        "y": float(parts[1].strip())
                    }
                else:
                    current_location = {"x": 0.0, "y": 0.0}
            except Exception:
                current_location = {"x": 0.0, "y": 0.0}
            vehicle_data["current_location"] = current_location

            # status: status_id를 문자열 상태로 매핑
            status_id = vehicle_data.get("status_id")
            vehicle_data["status"] = status_mapping.get(status_id, "Unknown")

            converted_vehicles.append(vehicle_data)

        from app.api.schemas.admin.vehicle_shema import VehicleItem
        vehicle_items = [VehicleItem.parse_obj(v) for v in converted_vehicles]

        vehicles_data = VehiclesData(
            vehicles=vehicle_items,
            pagination=paginated_result["pagination"]
        )

        return VehiclesResponse.success(
            data=vehicles_data,
            message="Vehicle data retrieved successfully"
        )