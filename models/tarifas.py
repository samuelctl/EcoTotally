from sqlalchemy import Column, Integer, String, Numeric, ForeignKey    
from database.connection import Base
from sqlalchemy.orm import relationship

class Tarifa(Base):
    __tablename__ = "tarifas"
    
    id_tarifa = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), nullable=False)
    unidade = Column(String(20))
    valor = Column(Numeric(10,2), nullable=False)
    regiao = Column(String(50), nullable=False)