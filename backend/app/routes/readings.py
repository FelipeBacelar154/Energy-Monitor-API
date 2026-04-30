"""
readings.py
-----------
Rotas de leituras (PROTEGIDAS + MULTI-USER)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime

from app.config.database import get_db
from app.models.models import Reading, Equipment, User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/readings", tags=["Readings"])

COST_PER_KWH = 0.75


# ================= SCHEMA =================
class ReadingInput(BaseModel):
    equipment_id: int
    consumption_kwh: float
    voltage: float | None = None
    current: float | None = None


# ================= CREATE =================
@router.post("/")
def add_reading(
    data: ReadingInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipment = db.query(Equipment).filter(
        Equipment.id == data.equipment_id,
        Equipment.user_id == current_user.id
    ).first()

    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    reading = Reading(
        equipment_id=data.equipment_id,
        consumption_kwh=data.consumption_kwh,
        voltage=data.voltage,
        current=data.current,
        timestamp=datetime.utcnow()
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return reading


# ================= LIST BY EQUIPMENT =================
@router.get("/{equipment_id}")
def get_readings(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.user_id == current_user.id
    ).first()

    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return db.query(Reading).filter(
        Reading.equipment_id == equipment_id
    ).order_by(Reading.timestamp.desc()).all()


# ================= DASHBOARD =================
@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipments = db.query(Equipment).filter(
        Equipment.user_id == current_user.id
    ).all()

    equipment_ids = [e.id for e in equipments]

    total_consumption = db.query(
        func.sum(Reading.consumption_kwh)
    ).filter(
        Reading.equipment_id.in_(equipment_ids)
    ).scalar() or 0

    total_cost = round(total_consumption * COST_PER_KWH, 2)

    # Top consumer
    top = db.query(
        Equipment.name,
        func.sum(Reading.consumption_kwh).label("total")
    ).join(Reading).filter(
        Equipment.user_id == current_user.id
    ).group_by(Equipment.id).order_by(
        func.sum(Reading.consumption_kwh).desc()
    ).first()

    return {
        "total_equipments": len(equipments),
        "total_consumption_kwh": round(total_consumption, 2),
        "total_cost_brl": total_cost,
        "top_consumer": top.name if top else None
    }