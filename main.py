import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine, Base

from models.usuario import Usuario
from schemas.usuario import UsuarioResponse
from routers.usuario import router as usuario_router
from routers.login import router as login_router
from routers.simulacao import router as simulacao_router
from routers.consumo import router as consumo_router
from routers.metas import router as metas_router
from routers.insights import router as insights_router
from routers.rec_senha import router as rec_senha_router
from routers.ia import router as ia_router
from routers.pdf import router as pdf_router
from routers.mapa import router as mapa_router

app = FastAPI(title="EcoTotally API", version="2.0.0")

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Em produção, liste aqui apenas os domínios reais do seu front-end.
# Aceita lista separada por vírgula via variável de ambiente ALLOWED_ORIGINS.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200,http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(usuario_router)
app.include_router(login_router, prefix="/login")
app.include_router(consumo_router)        # já tem prefix="/consumos" no próprio router
app.include_router(simulacao_router)      # já tem prefix="/simulacoes"
app.include_router(metas_router)          # já tem prefix="/metas"
app.include_router(insights_router)       # já tem prefix="/insights"
app.include_router(rec_senha_router, prefix="/login")
app.include_router(ia_router)             # já tem prefix="/ia"
app.include_router(pdf_router)            # já tem prefix="/pdf"
app.include_router(mapa_router)           # já tem prefix="/mapa"
