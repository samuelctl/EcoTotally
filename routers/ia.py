from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.chat_ia import ChatIARequest
from services.insights_service import gerar_insights_completos
from services.ia_service import gerar_resposta_chat_ia, gerar_recomendacao_ia
from core.auth import get_usuario_logado

router = APIRouter(prefix="/ia", tags=["IA"])


@router.post("/recomendacoes")
def recomendacoes_com_ia(
    meses_projetados: int = Query(3, ge=1, le=24),
    janela_meses: int = Query(3, ge=1, le=24),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    insights = gerar_insights_completos(
        db=db,
        usuario_id=usuario.id,
        meses_projetados=meses_projetados,
        janela_meses=janela_meses
    )

    analise_ia = gerar_recomendacao_ia(insights)

    return {
        "usuario_id": usuario.id,
        "insights": insights,
        "analise_ia": analise_ia
    }


@router.post("/chat")
def conversar_com_ia(
    dados: ChatIARequest,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    insights = gerar_insights_completos(
        db=db,
        usuario_id=usuario.id,
        meses_projetados=3,
        janela_meses=3
    )
    resposta = gerar_resposta_chat_ia(
    insights=insights,
    pergunta=dados.pergunta,
    historico=dados.historico
)
    return {
        "resposta": resposta,
        "pergunta": dados.pergunta
    }