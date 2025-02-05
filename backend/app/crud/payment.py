from app.models.payment import Payment
from app.crud.base import CRUDBase

class PaymentCRUD(CRUDBase[Payment]):
    def __init__(self):
        super().__init__(Payment, "payment_id")
    
    def get_payment_status_name(self, status_id: int) -> str:
        """
        주어진 결제 상태 ID에 해당하는 이름을 반환합니다.
        """
        from app.crud.lut import get_payment_status_mapping
        mapping = get_payment_status_mapping()
        return mapping.get(status_id, "Unknown")

    def get_payment_method_name(self, method_id: int) -> str:
        """
        주어진 결제 방식 ID에 해당하는 이름을 반환합니다.
        """
        from app.crud.lut import get_payment_method_mapping
        mapping = get_payment_method_mapping()
        return mapping.get(method_id, "Unknown")

payment_crud = PaymentCRUD()