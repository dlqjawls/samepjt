from typing import Any, Dict
from fastapi import HTTPException
from sqlmodel import select
from app.core.database import get_session
from app.dummy_data import (
    dummy_admins, dummy_users, dummy_vehicles, dummy_modules,
    dummy_option_types, dummy_options, dummy_module_sets,
    dummy_module_set_option_types, dummy_module_maintenance,
    dummy_option_maintenance, dummy_vehicles_maintenance,
    dummy_vehicles_usage_history, dummy_module_usage_history,
    dummy_option_usage_history, dummy_rent_history,
    dummy_payments, dummy_video_storage
)

from app.models import (
    Admin, User, Vehicle, Module, OptionType, Option, 
    ModuleSet, ModuleSetOptionType, ModuleMaintenance, 
    OptionMaintenance, VehicleMaintenance, VehicleUsageHistory,
    ModuleUsageHistory, OptionUsageHistory, RentHistory, 
    Payment, VideoStorage
)

import logging

def insert_dummy_data():
    session = next(get_session())  
    try:
        # Insert dummy data for each model
        session.add_all([Admin(**data) for data in dummy_admins])
        session.add_all([User(**data) for data in dummy_users])
        session.add_all([Vehicle(**data) for data in dummy_vehicles])
        session.add_all([Module(**data) for data in dummy_modules])
        session.add_all([OptionType(**data) for data in dummy_option_types])
        session.add_all([Option(**data) for data in dummy_options])
        session.add_all([ModuleSet(**data) for data in dummy_module_sets])
        session.add_all([ModuleSetOptionType(**data) for data in dummy_module_set_option_types])
        session.add_all([ModuleMaintenance(**data) for data in dummy_module_maintenance])
        session.add_all([OptionMaintenance(**data) for data in dummy_option_maintenance])
        session.add_all([VehicleMaintenance(**data) for data in dummy_vehicles_maintenance])
        session.add_all([VehicleUsageHistory(**data) for data in dummy_vehicles_usage_history])
        session.add_all([ModuleUsageHistory(**data) for data in dummy_module_usage_history])
        session.add_all([OptionUsageHistory(**data) for data in dummy_option_usage_history])
        session.add_all([RentHistory(**data) for data in dummy_rent_history])
        session.add_all([Payment(**data) for data in dummy_payments])
        session.add_all([VideoStorage(**data) for data in dummy_video_storage])

        # Commit the changes
        session.commit()
        logging.info("All dummy data inserted successfully.")
    
    except Exception as e:
        session.rollback()
        logging.error(f"Error inserting dummy data: {e}")


            
def get_all_data():
    """모든 테이블의 데이터를 조회합니다."""
    try:
        with get_session() as session:
            data = {
                "admins": session.exec(select(Admin)).all(),
                "users": session.exec(select(User)).all(),
                "vehicles": session.exec(select(Vehicle)).all(),
                "modules": session.exec(select(Module)).all(),
                "option_types": session.exec(select(OptionType)).all(),
                "options": session.exec(select(Option)).all(),
                "module_sets": session.exec(select(ModuleSet)).all(),
                "module_set_option_types": session.exec(select(ModuleSetOptionType)).all(),
                "module_maintenance": session.exec(select(ModuleMaintenance)).all(),
                "option_maintenance": session.exec(select(OptionMaintenance)).all(),
                "vehicle_maintenance": session.exec(select(VehicleMaintenance)).all(),
                "vehicle_usage_history": session.exec(select(VehicleUsageHistory)).all(),
                "module_usage_history": session.exec(select(ModuleUsageHistory)).all(),
                "option_usage_history": session.exec(select(OptionUsageHistory)).all(),
                "rent_history": session.exec(select(RentHistory)).all(),
                "payments": session.exec(select(Payment)).all(),
                "video_storage": session.exec(select(VideoStorage)).all()
            }
            return data
    except Exception as e:
        logging.error(f"데이터 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail="데이터베이스 조회 중 오류가 발생했습니다."
        )
    

def get_table_data(table_name: str) -> Dict[str, Any]:
    """특정 테이블의 데이터를 조회합니다."""
    from app.models import (
        Admin, User, Vehicle, Module, OptionType, Option, 
        ModuleSet, ModuleSetOptionType, ModuleMaintenance,
        OptionMaintenance, VehicleMaintenance, VehicleUsageHistory,
        ModuleUsageHistory, OptionUsageHistory, RentHistory,
        Payment, VideoStorage
    )
    
    table_map = {
        "admin": Admin,
        "user": User,
        "vehicle": Vehicle,
        "module": Module,
        "option_type": OptionType,
        "option": Option,
        "module_set": ModuleSet,
        "module_set_option_type": ModuleSetOptionType,
        "module_maintenance": ModuleMaintenance,
        "option_maintenance": OptionMaintenance,
        "vehicle_maintenance": VehicleMaintenance,
        "vehicle_usage_history": VehicleUsageHistory,
        "module_usage_history": ModuleUsageHistory,
        "option_usage_history": OptionUsageHistory,
        "rent_history": RentHistory,
        "payment": Payment,
        "video_storage": VideoStorage
    }

    model = table_map.get(table_name.lower())
    if not model:
        return {"error": f"Table '{table_name}' not found"}

    try:
        with get_session() as session:
            results = session.exec(select(model)).all()
            return {table_name: [result.dict() for result in results]}
    except Exception as e:
        logging.error(f"Error querying table {table_name}: {e}")
        return {"error": f"Error querying table '{table_name}'"}