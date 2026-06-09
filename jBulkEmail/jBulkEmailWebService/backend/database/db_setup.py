import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'jbes.db')}")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database Tables Initialized.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
