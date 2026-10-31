import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

ACADEMY_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "academy.db")
)
os.makedirs(os.path.dirname(ACADEMY_DB_PATH), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{ACADEMY_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
