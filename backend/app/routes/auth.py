"""
auth.py
-------
Rotas de autenticação — cadastro e login.

Rotas:
- POST /auth/register → cria conta
- POST /auth/login    → faz login e retorna token
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.config.database import get_db
from app.services import auth_service

router = APIRouter()

class RegisterInput(BaseModel):
    name: str
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

@router.post("/register", status_code=201)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    user, error = auth_service.register_user(db, data.name, data.email, data.password)
    if error:
        return {"success": False, "error": error}
    return {"success": True, "data": {"message": "Account created!", "id": user.id}}

@router.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    result, error = auth_service.login_user(db, data.email, data.password)
    if error:
        return {"success": False, "error": error}
    return {"success": True, "data": result}