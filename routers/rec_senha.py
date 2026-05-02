import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.email import enviar_email
from core.security import criar_token_recuperacao, verificar_token, gerar_hash_senha
from database.connection import get_db
from schemas.rec_senha import EsqueciSenhaRequest, RedefinirSenhaRequest
from models.usuario import Usuario

router = APIRouter(tags=["Recuperar Senha"])

# URL base do front-end — configure via variável de ambiente em produção
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")


@router.post("/esqueci-senha")
def esqueci_senha(dados: EsqueciSenhaRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    # Resposta genérica — não revela se o email existe
    if not usuario:
        return {"mensagem": "Se o email existir, um link será enviado."}

    token = criar_token_recuperacao(usuario.id, usuario.email)
    link = f"{FRONTEND_URL}/redefinir-senha?token={token}"

    mensagem = f"""
<div style="background-color:#F1F8F4; padding:40px 0; font-family:Arial, sans-serif;">
    <div style="max-width:520px; margin:auto; background:#FFFFFF; border-radius:14px; padding:35px; box-shadow:0 6px 20px rgba(0,0,0,0.05);">
        <div style="text-align:center; margin-bottom:20px;">
            <h2 style="color:#1B5E20; margin:0;">🌳 EcoTotally</h2>
            <p style="color:#777; font-size:13px; margin-top:5px;">Controle inteligente de gastos</p>
        </div>
        <h3 style="color:#2E7D32; text-align:center; margin-bottom:20px;">Recuperação de senha</h3>
        <p style="color:#444; font-size:15px;">Olá, <strong>{usuario.nome}</strong></p>
        <p style="color:#555; font-size:15px; line-height:1.6;">
            Recebemos uma solicitação para redefinir sua senha. Para continuar, clique no botão abaixo:
        </p>
        <div style="text-align:center; margin:30px 0;">
            <a href="{link}"
               style="background:linear-gradient(135deg,#2E7D32,#1B5E20);color:white;padding:14px 30px;
                      text-decoration:none;border-radius:10px;font-size:16px;font-weight:bold;
                      display:inline-block;box-shadow:0 4px 12px rgba(46,125,50,0.3);">
                Redefinir senha
            </a>
        </div>
        <div style="background:#E8F5E9; padding:15px; border-radius:8px;">
            <p style="margin:0; font-size:14px; color:#2E7D32;">⚠️ Este link expira em 30 minutos.</p>
        </div>
        <p style="color:#777; font-size:13px; margin-top:20px; text-align:center;">
            Se você não solicitou essa alteração, ignore este email com segurança.
        </p>
        <hr style="border:none; border-top:1px solid #eee; margin:25px 0;">
        <p style="text-align:center; font-size:12px; color:#999;">© 2026 EcoTotally • Todos os direitos reservados</p>
    </div>
</div>
"""

    try:
        enviar_email(
            destinatario=usuario.email,
            assunto="Recuperação de senha — EcoTotally",
            mensagem_html=mensagem
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {str(e)}")

    return {"mensagem": "Se o email existir, um link será enviado."}


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenhaRequest, db: Session = Depends(get_db)):
    payload = verificar_token(dados.token)

    if not payload:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    if payload.get("type") != "reset_password":
        raise HTTPException(status_code=400, detail="Token inválido para redefinição de senha")

    usuario_id = payload.get("sub")
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Token sem usuário válido")

    # Validação mínima de senha
    if len(dados.nova_senha) < 6:
        raise HTTPException(status_code=422, detail="A nova senha deve ter pelo menos 6 caracteres")

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.senha = gerar_hash_senha(dados.nova_senha)
    db.commit()

    return {"mensagem": "Senha redefinida com sucesso"}
