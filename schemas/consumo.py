from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ConsumoCreate(BaseModel):
    tipo: str
    gasto: float
    data: datetime
    meta_id: Optional[int] = None