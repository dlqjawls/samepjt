# app/core/database.py
import os
from sqlmodel import SQLModel, create_engine, Session, select
from app.dummy_data import (
    dummy_admins,
    dummy_users,
    dummy_vehicles,
    dummy_modules,
    dummy_option_types,
    dummy_options,
    dummy_module_sets,
    dummy_module_set_option_types,
    dummy_module_maintenance,
    dummy_option_maintenance,
    dummy_vehicles_maintenance,
    dummy_vehicles_usage_history,
    dummy_module_usage_history,
    dummy_option_usage_history,
    dummy_rent_history,
    dummy_payments,
    dummy_video_storage,
)
from app.models.admin import Admin
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.vehicle_maintenance import VehicleMaintenance
from app.models.vehicle_usage_history import VehicleUsageHistory
from app.models.module import Module
from app.models.module_maintenance import ModuleMaintenance
from app.models.module_usage_history import ModuleUsageHistory
from app.models.option import Option
from app.models.option_maintenance import OptionMaintenance
from app.models.option_usage_history import OptionUsageHistory
from app.models.option_type import OptionType
from app.models.module_set import ModuleSet
from app.models.module_set_option_type import ModuleSetOptionType
from app.models.rent_history import RentHistory
from app.models.payment import Payment
from app.models.video_storage import VideoStorage
import logging

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def insert_dummy_data():
    with get_session() as session:
        try:
            # 더미 데이터를 SQLAlchemy 모델 인스턴스로 변환하여 추가
            session.add_all([Admin(**admin) for admin in dummy_admins])
            session.add_all([User(**user) for user in dummy_users])
            session.add_all([Vehicle(**vehicle) for vehicle in dummy_vehicles])
            session.add_all([Module(**module) for module in dummy_modules])
            session.add_all([OptionType(**option_type) for option_type in dummy_option_types])
            session.add_all([Option(**option) for option in dummy_options])
            session.add_all([ModuleSet(**module_set) for module_set in dummy_module_sets])
            session.add_all([ModuleSetOptionType(**module_set_option_type) for module_set_option_type in dummy_module_set_option_types])
            session.add_all([ModuleMaintenance(**module_maintenance) for module_maintenance in dummy_module_maintenance])
            session.add_all([OptionMaintenance(**option_maintenance) for option_maintenance in dummy_option_maintenance])
            session.add_all([VehicleMaintenance(**vehicle_maintenance) for vehicle_maintenance in dummy_vehicles_maintenance])
            session.add_all([VehicleUsageHistory(**vehicle_usage_history) for vehicle_usage_history in dummy_vehicles_usage_history])
            session.add_all([ModuleUsageHistory(**module_usage_history) for module_usage_history in dummy_module_usage_history])
            session.add_all([OptionUsageHistory(**option_usage_history) for option_usage_history in dummy_option_usage_history])
            session.add_all([RentHistory(**rent_history) for rent_history in dummy_rent_history])
            session.add_all([Payment(**payment) for payment in dummy_payments])
            session.add_all([VideoStorage(**video_storage) for video_storage in dummy_video_storage])

            session.commit()
            logging.info("Dummy data inserted successfully.")
        except Exception as e:
            session.rollback()
            logging.error(f"Error inserting dummy data: {e}")
        finally:
            session.close()

def initialize_database():
    if not os.path.exists("./test.db"):
        create_db_and_tables()
        insert_dummy_data()
    else:
        logging.info("Database already exists. Skipping creation and dummy data insertion.")


def get_all_data():
    with get_session() as session:
        admins = session.exec(select(Admin)).all()
        users = session.exec(select(User)).all()
        vehicles = session.exec(select(Vehicle)).all()
        modules = session.exec(select(Module)).all()
        options = session.exec(select(Option)).all()
        module_sets = session.exec(select(ModuleSet)).all()
        
        return {
            "admins": admins,
            "users": users,
            "vehicles": vehicles,
            "modules": modules,
            "options": options,
            "module_sets": module_sets
        }