"""
equipment_service.py
--------------------
Contém a lógica de negócio para gerenciar equipamentos elétricos.
O controller (route) chama o service, e o service acessa o banco.

Operações disponíveis:
- Listar todos os equipamentos
- Buscar equipamento por ID
- Criar novo equipamento
- Atualizar equipamento
- Deletar equipamento
"""

from sqlalchemy.orm import Session
from app.models.models import Equipment

def get_all_equipments(db: Session):
    """Retorna todos os equipamentos cadastrados."""
    return db.query(Equipment).all()

def get_equipment_by_id(db: Session, equipment_id: int):
    """Retorna um equipamento pelo ID."""
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()

def create_equipment(db: Session, name: str, power_kw: float, location: str, description: str = None):
    """
    Cria um novo equipamento no banco de dados.
    
    Parâmetros:
        name: nome do equipamento (ex: Motor 1)
        power_kw: potência em kW (ex: 5.5)
        location: localização (ex: Setor A)
        description: descrição opcional
    """
    equipment = Equipment(
        name=name,
        power_kw=power_kw,
        location=location,
        description=description
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment

def update_equipment(db: Session, equipment_id: int, name: str, power_kw: float, location: str, description: str = None):
    """Atualiza um equipamento existente."""
    equipment = get_equipment_by_id(db, equipment_id)
    if not equipment:
        return None

    equipment.name = name
    equipment.power_kw = power_kw
    equipment.location = location
    equipment.description = description

    db.commit()
    db.refresh(equipment)
    return equipment

def delete_equipment(db: Session, equipment_id: int):
    """Deleta um equipamento pelo ID."""
    equipment = get_equipment_by_id(db, equipment_id)
    if not equipment:
        return False

    db.delete(equipment)
    db.commit()
    return True