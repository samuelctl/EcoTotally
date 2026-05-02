import os
import tempfile
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from services.insights_service import gerar_insights_completos
from services.pdf_services import gerar_pdf_relatorio
from core.auth import get_usuario_logado

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.get("/relatorio")
def gerar_relatorio_pdf(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    insights = gerar_insights_completos(
        db=db,
        usuario_id=usuario.id,
        meses_projetados=3,
        janela_meses=3
    )

    # Usa arquivo temporário — não deixa lixo no disco após o envio
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()

    try:
        gerar_pdf_relatorio(insights, tmp.name)
        return FileResponse(
            path=tmp.name,
            filename="relatorio_ecototally.pdf",
            media_type="application/pdf",
            background=None  # FileResponse fecha o arquivo; limpamos abaixo via headers
        )
    except Exception:
        os.unlink(tmp.name)
        raise
