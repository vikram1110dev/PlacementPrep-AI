import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    logo_url = Column(String(255))
    website_url = Column(String(255))
    hiring_process = Column(JSON) # e.g. ["Aptitude", "Technical", "HR"]
    eligibility_criteria = Column(Text)
    industry_type = Column(String(100), default="Product Based") # e.g. "Product Based", "Service Based"
    tier = Column(String(50), default="Standard") # e.g. "Dream", "Standard"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class SystemSetting(Base):
    __tablename__ = 'system_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key_name = Column(String(100), unique=True, nullable=False)
    value_data = Column(JSON, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    admin_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(255), nullable=False) # e.g., "SUSPEND_USER"
    entity = Column(String(100)) # e.g., "User"
    entity_id = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())

class AIPromptConfiguration(Base):
    __tablename__ = 'ai_prompts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), unique=True, nullable=False)
    system_prompt = Column(Text, nullable=False)
    temperature = Column(String(10), default="0.7")
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="SYSTEM") # SYSTEM, PLACEMENT, ALERT
    target_role = Column(String(50)) # e.g., "STUDENT", "ALL"
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
