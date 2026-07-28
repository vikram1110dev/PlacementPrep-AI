from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.dependencies.auth import get_current_user, RoleChecker
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.admin import (
    AdminDashboardStats, AdminUserAction, CompanyCreate, CompanyResponse,
    SystemSettingUpdate, SystemSettingResponse, AuditLogResponse
)
from app.services.admin_service import AdminService

# Protect all routes by default
router = APIRouter(prefix="/admin", tags=["Enterprise Admin"], dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])

@router.get("/dashboard", response_model=StandardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    service = AdminService(db)
    metrics = service.get_dashboard_metrics()
    return StandardResponse(success=True, message="Dashboard loaded", data=metrics)

# --- Users ---
@router.post("/users/{target_user_id}/action", response_model=StandardResponse)
def manage_user(target_user_id: str, payload: AdminUserAction, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    user = service.handle_user_action(current_user.id, target_user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")
    return StandardResponse(success=True, message=f"User {payload.action} successful")

# --- Companies ---
@router.post("/companies", response_model=StandardResponse)
def create_company(payload: CompanyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    company = service.create_company(current_user.id, payload)
    return StandardResponse(success=True, message="Company created", data={"id": company.id})

@router.get("/companies", response_model=StandardResponse)
def get_companies(db: Session = Depends(get_db)):
    service = AdminService(db)
    return StandardResponse(success=True, message="Companies fetched", data=service.get_companies())

# --- Settings ---
@router.put("/settings", response_model=StandardResponse)
def update_setting(payload: SystemSettingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    service.update_system_setting(current_user.id, payload)
    return StandardResponse(success=True, message="Setting updated")

# --- Audit Logs ---
@router.get("/audit-logs", response_model=StandardResponse)
def get_audit_logs(skip: int = Query(0), limit: int = Query(50), db: Session = Depends(get_db)):
    service = AdminService(db)
    logs = service.get_audit_logs(skip, limit)
    return StandardResponse(success=True, message="Audit logs fetched", data=logs)
