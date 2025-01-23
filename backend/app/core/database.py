from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)