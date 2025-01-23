import os
import logging
from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

# FastAPI에서 의존성 주입을 위해 yield 사용
def get_session():
    with Session(engine) as session:
        yield session  # 요청이 끝나면 자동으로 닫힘

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def initialize_database():
    if not os.path.isfile("test.db"):
        create_db_and_tables()
        logging.info("Database tables created successfully.")
    else:
        logging.info("Database already exists. Skipping creation.")
