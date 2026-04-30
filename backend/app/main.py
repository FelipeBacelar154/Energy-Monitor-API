"""
main.py
-------
Ponto de entrada da API Energy Monitor.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import engine, Base
from app.routes import equipments, readings, reports, auth


# ================= LIFESPAN =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# ================= APP =================
app = FastAPI(
    title="Energy Monitor API",
    description="API para monitoramento de consumo de energia elétrica industrial",
    version="1.0.0",
    lifespan=lifespan,
)


# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ================= ROUTES =================
app.include_router(auth.router)
app.include_router(equipments.router)
app.include_router(readings.router)
app.include_router(reports.router)


# ================= HEALTH =================
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ================= ROOT =================
@app.get("/", tags=["Root"])
def root():
    return {"message": "Energy Monitor API is running!"}