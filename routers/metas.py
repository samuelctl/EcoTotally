from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.metas import Meta
from schemas.metas import MetasCreate, MetasResponse
from core.auth import get_usuario_logado

router = APIRouter(prefix="/metas", tags=["Metas"])


@router.post("/", response_model=MetasResponse)
def criar_meta(
    dados: MetasCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    nova_meta = Meta(
        tipo_meta=dados.tipo_meta,
        valor_objetivo=dados.valor_objetivo,
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim,
        usuario_id=usuario.id
    )

    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)

    return nova_meta


@router.get("/me", response_model=list[MetasResponse])
def listar_metas_usuario(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    metas = db.query(Meta).filter(Meta.usuario_id == usuario.id).all()
    return metas


@router.put("/{meta_id}", response_model=MetasResponse)
def editar_meta(
    meta_id: int,
    dados: MetasCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    meta = db.query(Meta).filter(
        Meta.id_meta == meta_id,
        Meta.usuario_id == usuario.id
    ).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    meta.tipo_meta = dados.tipo_meta
    meta.valor_objetivo = dados.valor_objetivo
    meta.data_inicio = dados.data_inicio
    meta.data_fim = dados.data_fim

    db.commit()
    db.refresh(meta)

    return meta


@router.delete("/{meta_id}")
def deletar_meta(
    meta_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    meta = db.query(Meta).filter(
        Meta.id_meta == meta_id,
        Meta.usuario_id == usuario.id
    ).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    db.delete(meta)
    db.commit()

    return {"detail": "Meta deletada com sucesso"}