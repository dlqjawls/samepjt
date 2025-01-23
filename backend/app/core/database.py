from sqlmodel import SQLModel, create_engine, Session
import os
import logging

# Database configuration
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def initialize_database():
    # 데이터베이스가 존재하지 않으면 테이블 생성
    if not os.path.exists("./test.db"):
        create_db_and_tables()
        logging.info("Database tables created successfully.")
    else:
        logging.info("Database already exists. Skipping creation.")