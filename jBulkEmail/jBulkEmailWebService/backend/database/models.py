from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    otp = Column(String, nullable=True)
    otp_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SenderProfile(Base):
    __tablename__ = 'sender_profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    app_password = Column(String, nullable=False) # DPAPI will be swapped for Web encryption
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")

class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, default="IDLE") # IDLE, PROCESSING, COMPLETED, HALTED
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    user = relationship("User")
    attachments = relationship("Attachment", back_populates="mission", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=False)
    filename = Column(String, nullable=False)
    s3_url = Column(String, nullable=True) # AWS S3 integration placeholder
    file_size = Column(Integer, nullable=False)
    
    mission = relationship("Mission", back_populates="attachments")
