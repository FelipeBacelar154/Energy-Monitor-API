"""
auth_service.py
---------------
Lógica de autenticação — cadastro, login, JWT e usuário atual.
"""

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.models import User
from app.config.database import get_db

# ================= CONFIG =================
SECRET_KEY = "energy-monitor-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# ================= PASSWORD =================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ================= JWT =================
def create_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ================= CURRENT USER =================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ================= REGISTER =================
def register_user(db: Session, name: str, email: str, password: str):
    existing = db.query(User).filter(User.email == email.lower()).first()

    if existing:
        return None, "Email already registered"

    if len(password) < 6:
        return None, "Password must be at least 6 characters"

    user = User(
        name=name.strip(),
        email=email.lower(),
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user, None


# ================= LOGIN =================
def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email.lower()).first()

    if not user:
        return None, "User not found"

    if not verify_password(password, user.password):
        return None, "Incorrect password"

    token = create_token(user.id, user.email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }, None