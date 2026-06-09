import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///C:/Users/dell/jAnitGravity/jBulkEmailSender/jBulkEmailWebService/backend/database/jbes.db")

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
