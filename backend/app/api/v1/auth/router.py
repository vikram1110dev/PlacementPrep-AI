from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.base import StandardResponse
from app.schemas.auth import UserCreate, UserLogin, RefreshTokenRequest, ForgotPasswordRequest, UserResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user, RoleChecker
from app.models.auth import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=StandardResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register_user(user_in)
    return StandardResponse(success=True, message="Registration successful", data=user)

@router.post("/login", response_model=StandardResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    result = service.authenticate_user(credentials, device_info=user_agent, ip_address=ip_address)
    return StandardResponse(success=True, message="Login successful", data=result)

@router.post("/refresh", response_model=StandardResponse)
def refresh_token(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.refresh_access_token(request_data.refresh_token)
    return StandardResponse(success=True, message="Token refreshed", data=result)

@router.post("/logout", response_model=StandardResponse)
def logout(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(request_data.refresh_token)
    return StandardResponse(success=True, message="Logged out successfully")

@router.post("/forgot-password", response_model=StandardResponse)
def forgot_password(request_data: ForgotPasswordRequest):
    # Placeholder for forgot password logic
    return StandardResponse(success=True, message="If email exists, reset instructions have been sent.")

# --- Protected Endpoints Example ---

@router.get("/me", response_model=StandardResponse)
def get_me(current_user: User = Depends(get_current_user)):
    roles = [r.name for r in current_user.roles]
    data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "roles": roles
    }
    return StandardResponse(success=True, message="Current user profile", data=data)

@router.get("/admin-only", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def admin_only_route():
    return StandardResponse(success=True, message="You have admin access!")
