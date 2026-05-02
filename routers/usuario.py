from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.usuario import UsuarioResponse, UsuarioCreate, DadosResponse
from models.usuario import Usuario
from core.security import gerar_hash_senha
from core.auth import get_usuario_logado
from routers import regiao

router = APIRouter(tags=["Usuarios"])


@router.post("/usuario", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if len(usuario.senha) < 6:
        raise HTTPException(status_code=422, detail="A senha deve ter pelo menos 6 caracteres")

    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = gerar_hash_senha(usuario.senha)

    localidade = regiao.get_regiao_por_cidade(usuario.cidade)
    nome_regiao = "Não informada"
    if localidade and isinstance(localidade, dict):
        nome_regiao = localidade.get("regiao", "Não encontrada")

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=senha_hash,
        cidade=usuario.cidade,
        regiao=nome_regiao
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.get("/usuario/me", response_model=DadosResponse)
def ver_meus_dados(usuario=Depends(get_usuario_logado)):
    return usuario


@router.put("/usuario/me", response_model=UsuarioResponse)
def editar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    usuario_com_mesmo_email = db.query(Usuario).filter(
        Usuario.email == dados.email,
        Usuario.id != usuario.id
    ).first()

    if usuario_com_mesmo_email:
        raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário")

    localidade = regiao.get_regiao_por_cidade(dados.cidade)
    nome_regiao = "Não informada"
    if localidade and isinstance(localidade, dict):
        nome_regiao = localidade.get("regiao", "Não encontrada")

    usuario.nome = dados.nome
    usuario.email = dados.email
    # Só atualiza senha se uma nova foi fornecida
    if dados.senha and len(dados.senha) >= 6:
        usuario.senha = gerar_hash_senha(dados.senha)
    elif dados.senha and len(dados.senha) < 6:
        raise HTTPException(status_code=422, detail="A senha deve ter pelo menos 6 caracteres")
    usuario.cidade = dados.cidade
    usuario.regiao = nome_regiao

    db.commit()
    db.refresh(usuario)

    return usuario


@router.delete("/usuario/me")
def deletar_usuario(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    db.delete(usuario)
    db.commit()
    return {"detail": "Usuário deletado com sucesso"}
