import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.auth import RefreshToken
import secrets

class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    def register_user(self, user_in: UserCreate):
        if self.repo.get_user_by_email(user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_pw = get_password_hash(user_in.password)
        student_role = self.repo.get_role_by_name('STUDENT')
        
        # In a real app, if role doesn't exist, you might need to seed it or throw error.
        user = self.repo.create_user(user_in, hashed_pw, student_role)
        
        # Note: In production, send verification email here
        
        # Format user response (extract role names)
        roles = [r.name for r in user.roles]
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "roles": roles
        }

    def authenticate_user(self, credentials: UserLogin, device_info: str = "", ip_address: str = ""):
        user = self.repo.get_user_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        # Generate Access Token
        access_token = create_access_token(subject=user.id)
        
        # Generate Refresh Token
        refresh_token_str = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        refresh_token = RefreshToken(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token=refresh_token_str,
            expires_at=expires_at
        )
        self.repo.save_refresh_token(refresh_token)
        
        # Track Session
        self.repo.create_session(user.id, device_info, ip_address)
        
        roles = [r.name for r in user.roles]
        
        return {
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token_str,
                "token_type": "bearer"
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "roles": roles
            }
        }
        
    def refresh_access_token(self, refresh_token_str: str):
        token_obj = self.repo.get_refresh_token(refresh_token_str)
        
        if not token_obj or token_obj.is_revoked:
            raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")
            
        if token_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")
            
        access_token = create_access_token(subject=token_obj.user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer"
        }
        
    def logout(self, refresh_token_str: str):
        token_obj = self.repo.get_refresh_token(refresh_token_str)
        if token_obj:
            self.repo.revoke_refresh_token(token_obj)
        return True
