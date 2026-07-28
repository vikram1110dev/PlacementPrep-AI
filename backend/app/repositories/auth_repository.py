from sqlalchemy.orm import Session
from app.models.auth import User, Role, RefreshToken, Session as DbSession
from app.schemas.auth import UserCreate
import uuid

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_role_by_name(self, role_name: str) -> Role:
        return self.db.query(Role).filter(Role.name == role_name).first()

    def create_user(self, user_in: UserCreate, hashed_password: str, default_role: Role) -> User:
        db_user = User(
            id=str(uuid.uuid4()),
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name
        )
        if default_role:
            db_user.roles.append(default_role)
            
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def save_refresh_token(self, token: RefreshToken):
        self.db.add(token)
        self.db.commit()
        
    def get_refresh_token(self, token_str: str) -> RefreshToken:
        return self.db.query(RefreshToken).filter(RefreshToken.token == token_str).first()
        
    def revoke_refresh_token(self, token_obj: RefreshToken):
        token_obj.is_revoked = True
        self.db.commit()

    def create_session(self, user_id: str, device_info: str, ip_address: str) -> DbSession:
        session = DbSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            device_info=device_info,
            ip_address=ip_address
        )
        self.db.add(session)
        self.db.commit()
        return session
