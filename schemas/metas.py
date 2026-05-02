from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class MetasBase(BaseModel):
    tipo_meta: str
    valor_objetivo: Decimal
    data_inicio: date
    data_fim: date


class MetasCreate(MetasBase):
    pass


class MetasResponse(MetasBase):
    id_meta: int
    usuario_id: int

    class Config:
        from_attributes = True