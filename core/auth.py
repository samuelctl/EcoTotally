from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.connection import get_db
from models.usuario import Usuario
from core.security import verificar_token

security = HTTPBearer()


def get_usuario_logado(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verificar_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    usuario_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return usuario