from fastapi import APIRouter, Depends
from core.auth import get_usuario_logado
from services.map_service import buscar_pontos

router = APIRouter(prefix="/mapa", tags=["Mapa"])


@router.get("/reciclagem")
def get_pontos(
    lat: float,
    lon: float,
    _usuario=Depends(get_usuario_logado)   # autenticação obrigatória
):
    return buscar_pontos(lat, lon)
