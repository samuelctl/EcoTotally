import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 dias   ← ALTERADO (era 120 / 2h)
RESET_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plain, senha_hash)


def criar_token_access(data: dict) -> str:
    dados = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def criar_token_recuperacao(usuario_id: int, email: str) -> str:
    dados = {
        "sub": str(usuario_id),
        "email": email,
        "type": "reset_password"
    }

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRE_MINUTES
    )

    dados.update({"exp": expire})

    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        usuario_id = payload.get("sub")

        if usuario_id is None:
            return None

        return payload

    except ExpiredSignatureError:
        print("Token expirado")
        return None

    except JWTError as e:
        print("Token inválido:", e)
        return None
