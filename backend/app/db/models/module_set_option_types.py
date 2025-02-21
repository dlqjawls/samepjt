from sqlmodel import SQLModel, Field

class ModuleSetOptionTypes(SQLModel, table=True):
    __tablename__ = "module_set_option_types"

    module_set_id: int = Field(foreign_key="module_set.module_set_id", primary_key=True, nullable=False, description="Module Set ID")
    option_type_id: int = Field(foreign_key="option_type.option_type_id", primary_key=True, nullable=False, description="Option Type ID")
    option_quantity: int = Field(nullable=False, description="Quantity of Option in the Set (>= 0)")