from sqlalchemy import Column, Integer, String, Numeric, ForeignKey    
from database.connection import Base
from sqlalchemy.orm import relationship

class Simulacao(Base):
    __tablename__ = "simulacao"
    id_simulacao = Column(Integer, primary_key=True, autoincrement=True)
    atividade = Column(String(120), nullable=False)
    tipo = Column(String(50), nullable=False)
    consumo_valor = Column(Numeric(10,2), nullable=False)
    valor_calculado = Column(Numeric(10,2), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="simulacoes")
    regiao_aplicada = Column(String(100), nullable=False)
    id_tarifa = Column(Integer, ForeignKey("tarifas.id_tarifa"))
    tarifa = relationship("Tarifa")
