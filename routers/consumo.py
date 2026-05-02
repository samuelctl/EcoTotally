from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.consumo import Consumo
from schemas.consumo import ConsumoCreate
from core.auth import get_usuario_logado
from models.metas import Meta

router = APIRouter(prefix="/consumos", tags=["Consumos"])


@router.post("/")
def criar_consumo(
    dados: ConsumoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    if dados.meta_id is not None:
        meta = db.query(Meta).filter(
            Meta.id_meta == dados.meta_id,
            Meta.usuario_id == usuario.id
        ).first()

        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada ou não pertence ao usuário")

    novo_cons = Consumo(
        tipo=dados.tipo,
        gasto=dados.gasto,
        data=dados.data,
        usuario_id=usuario.id,
        meta_id=dados.meta_id
    )

    db.add(novo_cons)
    db.commit()
    db.refresh(novo_cons)

    return {"status": "Consumo registrado com sucesso"}

@router.get("/me")
def listar_consumos(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    lista = db.query(Consumo).filter(
        Consumo.usuario_id == usuario.id
    ).all()

    return lista


@router.put("/{consumo_id}")
def editar_consumo(
    consumo_id: int,
    dados: ConsumoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    db_consumo = db.query(Consumo).filter(
        Consumo.id == consumo_id,
        Consumo.usuario_id == usuario.id
    ).first()

    if not db_consumo:
        raise HTTPException(status_code=404, detail="Consumo não encontrado")

    db_consumo.tipo = dados.tipo
    db_consumo.gasto = dados.gasto
    db_consumo.data = dados.data

    db.commit()
    db.refresh(db_consumo)

    return db_consumo


@router.delete("/{consumo_id}")
def deletar_consumo(
    consumo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    db_consumo = db.query(Consumo).filter(
        Consumo.id == consumo_id,
        Consumo.usuario_id == usuario.id
    ).first()

    if not db_consumo:
        raise HTTPException(status_code=404, detail="Consumo não encontrado")

    db.delete(db_consumo)
    db.commit()

    return {"detail": "Deletado com sucesso"}