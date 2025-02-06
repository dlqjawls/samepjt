from app.db.models.payment import Payment
from app.db.crud.base import CRUDBase

class PaymentCRUD(CRUDBase[Payment]):
    def __init__(self):
        super().__init__(Payment)
    

payment_crud = PaymentCRUD()