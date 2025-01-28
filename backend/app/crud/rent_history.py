from app.models.rent_history import RentHistory
from app.crud.base import CRUDBase

class RentHistoryCRUD(CRUDBase[RentHistory]):
    def __init__(self):
        super().__init__(RentHistory, "rent_id", soft_delete_field="status_id", soft_delete_value=3)

    
rent_history_crud = RentHistoryCRUD()