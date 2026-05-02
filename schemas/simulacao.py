from pydantic import BaseModel
from decimal import Decimal


class SimulacaoCreate(BaseModel):
    atividade: str
    tipo: str
    consumo_valor: Decimal