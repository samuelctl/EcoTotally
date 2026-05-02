from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from services.insights_service import gerar_insights_completos
from core.auth import get_usuario_logado

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/projecao")
def projecao_por_tipo_v2(
    meses_projetados: int = Query(3, ge=1, le=24),
    janela_meses: int = Query(3, ge=1, le=24),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    return gerar_insights_completos(
        db=db,
        usuario_id=usuario.id,  
        meses_projetados=meses_projetados,
        janela_meses=janela_meses
    )