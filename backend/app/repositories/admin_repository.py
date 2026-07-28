from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.auth import User, Role
from app.models.admin import Company, SystemSetting, AuditLog, Notification
from app.models.aptitude import AptitudeQuestion, MockTest
from app.schemas.admin import CompanyCreate, SystemSettingUpdate, NotificationCreate

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Dashboard Metrics ---
    def get_dashboard_metrics(self) -> dict:
        # These queries can be expensive on massive tables; caching in Redis in Service layer is ideal.
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        
        # Calculate daily active (users seen in last 24h)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        dau = self.db.query(func.count(User.id)).filter(User.last_login >= one_day_ago).scalar() or 0
        
        # Other entities
        total_companies = self.db.query(func.count(Company.id)).scalar() or 0
        total_mock_tests = self.db.query(func.count(MockTest.id)).scalar() or 0
        total_aptitude = self.db.query(func.count(AptitudeQuestion.id)).scalar() or 0
        
        return {
            "total_users": total_users,
            "daily_active_users": dau,
            "premium_users": 0, # Placeholder
            "total_companies": total_companies,
            "total_coding_problems": total_aptitude, # Merged metric for now
            "total_mock_tests": total_mock_tests,
            "total_projects": 0,
            "ai_requests_today": 1250, # Placeholder
            "revenue_usd": 0.0
        }

    # --- User Management ---
    def get_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user_status(self, user_id: str, is_active: bool) -> Optional[User]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = is_active
            self.db.commit()
            self.db.refresh(user)
        return user

    # --- Companies ---
    def get_companies(self) -> List[Company]:
        return self.db.query(Company).all()

    def create_company(self, payload: CompanyCreate) -> Company:
        company = Company(**payload.model_dump())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    # --- Audit Logs ---
    def log_action(self, admin_id: str, action: str, entity: str = None, entity_id: str = None, details: dict = None, ip_address: str = None):
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
        self.db.add(log)
        self.db.commit()
        
    def get_audit_logs(self, skip: int = 0, limit: int = 50) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    # --- Settings ---
    def get_settings(self) -> List[SystemSetting]:
        return self.db.query(SystemSetting).all()

    def update_setting(self, key_name: str, value_data: dict) -> SystemSetting:
        setting = self.db.query(SystemSetting).filter(SystemSetting.key_name == key_name).first()
        if not setting:
            setting = SystemSetting(key_name=key_name, value_data=value_data)
            self.db.add(setting)
        else:
            setting.value_data = value_data
        
        self.db.commit()
        self.db.refresh(setting)
        return setting
