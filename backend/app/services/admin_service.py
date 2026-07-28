from sqlalchemy.orm import Session
from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import CompanyCreate, SystemSettingUpdate, AdminUserAction
import json
import redis
from app.core.config import settings

class AdminService:
    def __init__(self, db: Session):
        self.repo = AdminRepository(db)
        try:
            self.redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        except Exception:
            self.redis_client = None

    def get_dashboard_metrics(self) -> dict:
        cache_key = "admin:dashboard:metrics"
        
        # Try to fetch from Redis Cache
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception:
                pass
                
        # Cache miss or no redis: Compute metrics
        metrics = self.repo.get_dashboard_metrics()
        
        # Set to Cache (expire in 5 minutes)
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, 300, json.dumps(metrics))
            except Exception:
                pass
                
        return metrics

    def handle_user_action(self, admin_id: str, target_user_id: str, payload: AdminUserAction):
        if payload.action == "SUSPEND" or payload.action == "DEACTIVATE":
            user = self.repo.update_user_status(target_user_id, is_active=False)
        elif payload.action == "ACTIVATE":
            user = self.repo.update_user_status(target_user_id, is_active=True)
            
        # Log Audit
        self.repo.log_action(
            admin_id=admin_id,
            action=payload.action,
            entity="User",
            entity_id=target_user_id,
            details={"reason": payload.reason}
        )
        return user

    def create_company(self, admin_id: str, payload: CompanyCreate):
        company = self.repo.create_company(payload)
        self.repo.log_action(admin_id, "CREATE_COMPANY", "Company", str(company.id), payload.model_dump())
        return company

    def get_companies(self):
        return self.repo.get_companies()

    def update_system_setting(self, admin_id: str, payload: SystemSettingUpdate):
        setting = self.repo.update_setting(payload.key_name, payload.value_data)
        self.repo.log_action(admin_id, "UPDATE_SETTING", "SystemSetting", payload.key_name, payload.value_data)
        return setting

    def get_audit_logs(self, skip: int = 0, limit: int = 50):
        return self.repo.get_audit_logs(skip, limit)
