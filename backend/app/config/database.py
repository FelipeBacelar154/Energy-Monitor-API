"""
database.py
-----------
Configuração de banco de dados (SQLite local + PostgreSQL produção).

Funciona assim:
- Local: usa SQLite automaticamente
- Produção (Render): usa DATABASE_URL (PostgreSQL)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ================= DATABASE URL =================

DATABASE_URL = os.getenv("DATABASE_URL")

# Se NÃO existir variável (local), usa SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./energy_monitor.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Render usa postgres:// → SQLAlchemy precisa postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

    engine = create_engine(DATABASE_URL)


# ================= SESSION =================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ================= BASE =================

Base = declarative_base()


# ================= DEPENDENCY =================

def get_db():
    """
    Cria e fecha sessão automaticamente (FastAPI dependency)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()