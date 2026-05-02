from pydantic import BaseModel, EmailStr
from typing import Optional


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cidade: str


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    regiao: str

    class Config:
        from_attributes = True


class DadosResponse(BaseModel):
    id: int
    nome: str
    email: str
    cidade: Optional[str] = None
    regiao: Optional[str] = None

    class Config:
        from_attributes = True
