from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Dashboard ---
class AdminDashboardStats(BaseModel):
    total_users: int
    daily_active_users: int
    premium_users: int
    total_companies: int
    total_coding_problems: int
    total_mock_tests: int
    total_projects: int
    ai_requests_today: int
    revenue_usd: float

# --- User Management ---
class AdminUserAction(BaseModel):
    action: str # SUSPEND, ACTIVATE, DEACTIVATE
    reason: Optional[str] = None

class AdminAssignRole(BaseModel):
    role_name: str

# --- Company ---
class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    hiring_process: List[str] = []
    eligibility_criteria: Optional[str] = None
    is_active: bool = True

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    class Config: from_attributes = True

# --- Settings ---
class SystemSettingUpdate(BaseModel):
    key_name: str
    value_data: Dict[str, Any]

class SystemSettingResponse(BaseModel):
    key_name: str
    value_data: Dict[str, Any]
    class Config: from_attributes = True

# --- Audit Logs ---
class AuditLogResponse(BaseModel):
    id: str
    admin_id: Optional[str]
    action: str
    entity: Optional[str]
    entity_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime
    class Config: from_attributes = True

# --- Notifications ---
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "SYSTEM"
    target_role: Optional[str] = "ALL"
