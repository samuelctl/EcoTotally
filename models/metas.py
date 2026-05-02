from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database.connection import Base


class Meta(Base):
    __tablename__ = "metas"

    id_meta = Column(Integer, primary_key=True, autoincrement=True)
    tipo_meta = Column(String(50), nullable=False)
    valor_objetivo = Column(Numeric(10, 2), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="metas")
    consumos = relationship("Consumo", back_populates="meta")