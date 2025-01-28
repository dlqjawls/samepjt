from app.models.payment import Payment
from app.crud.base import CRUDBase

class PaymentCRUD(CRUDBase[Payment]):
    def __init__(self):
        super().__init__(Payment, "payment_id")
    
payment_crud = PaymentCRUD()