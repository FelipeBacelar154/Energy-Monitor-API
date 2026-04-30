"""
equipments.py
-------------
Rotas de equipamentos (PROTEGIDAS + MULTI-USER)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config.database import get_db
from app.models.models import Equipment, User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/equipments", tags=["Equipments"])


# ================= SCHEMA =================
class EquipmentInput(BaseModel):
    name: str
    power_kw: float
    location: str
    description: str | None = None


# ================= LIST =================
@router.get("/")
def list_equipments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Equipment).filter(
        Equipment.user_id == current_user.id
    ).all()


# ================= CREATE =================
@router.post("/")
def create_equipment(
    data: EquipmentInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    eq = Equipment(
        name=data.name,
        power_kw=data.power_kw,
        location=data.location,
        description=data.description,
        user_id=current_user.id
    )

    db.add(eq)
    db.commit()
    db.refresh(eq)

    return eq


# ================= DELETE =================
@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    eq = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.user_id == current_user.id
    ).first()

    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    db.delete(eq)
    db.commit()

    return {"message": "Equipment deleted"}