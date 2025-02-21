from decimal import Decimal
from pydantic import BaseModel

from app.api.schemas.common import ResponseBase

class ModuleType(BaseModel):
    module_type_id: int
    module_type_name: str
    module_type_size: str
    module_type_cost: Decimal
    
    class Config:
        orm_mode = True
        
class ModuleTypesData(BaseModel):
    module_types: list[ModuleType]

class ModuleTypesResponse(ResponseBase[ModuleTypesData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Module types retrieved successfully",
                "data": {
                    "module_types": [
                        {
                            "module_type_id": 1,
                            "module_type_name": "Module Type 1",
                            "module_type_size": "100x100",
                            "module_type_cost": 100.00
                        }
                    ]
                }     
            }
        }
