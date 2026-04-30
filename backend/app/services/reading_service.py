"""
reading_service.py
------------------
Contém a lógica de negócio para gerenciar leituras de consumo.
Também calcula estatísticas e custos de energia.

Operações disponíveis:
- Registrar nova leitura
- Listar leituras por equipamento
- Calcular consumo total
- Calcular custo estimado
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Reading, Equipment
from datetime import datetime

# Custo médio do kWh no Brasil (R$)
COST_PER_KWH = 0.75

def get_readings_by_equipment(db: Session, equipment_id: int, limit: int = 50):
    """Retorna as últimas leituras de um equipamento."""
    return db.query(Reading)\
        .filter(Reading.equipment_id == equipment_id)\
        .order_by(Reading.timestamp.desc())\
        .limit(limit)\
        .all()

def create_reading(db: Session, equipment_id: int, consumption_kwh: float, voltage: float = None, current: float = None):
    """
    Registra uma nova leitura de consumo.

    Parâmetros:
        equipment_id: ID do equipamento
        consumption_kwh: consumo em kWh
        voltage: tensão em V (opcional)
        current: corrente em A (opcional)
    """
    reading = Reading(
        equipment_id=equipment_id,
        consumption_kwh=consumption_kwh,
        voltage=voltage,
        current=current
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

def get_total_consumption(db: Session, equipment_id: int):
    """Calcula o consumo total de um equipamento."""
    result = db.query(func.sum(Reading.consumption_kwh))\
        .filter(Reading.equipment_id == equipment_id)\
        .scalar()
    return round(result or 0, 2)

def get_estimated_cost(db: Session, equipment_id: int):
    """Calcula o custo estimado de energia de um equipamento."""
    total = get_total_consumption(db, equipment_id)
    return round(total * COST_PER_KWH, 2)

def get_dashboard_stats(db: Session):
    """
    Retorna estatísticas gerais para o dashboard.
    """
    total_equipments = db.query(Equipment).count()

    total_consumption = db.query(func.sum(Reading.consumption_kwh)).scalar() or 0
    total_consumption = round(total_consumption, 2)

    total_cost = round(total_consumption * COST_PER_KWH, 2)

    top_equipment = db.query(
        Equipment.name,
        func.sum(Reading.consumption_kwh).label("total")
    ).join(Reading)\
     .group_by(Equipment.id)\
     .order_by(func.sum(Reading.consumption_kwh).desc())\
     .first()

    return {
        "total_equipments": total_equipments,
        "total_consumption_kwh": total_consumption,
        "total_cost_brl": total_cost,
        "top_consumer": top_equipment.name if top_equipment else None
    }