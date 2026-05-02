from sqlalchemy import Column, Integer, String, DateTime,Numeric, ForeignKey    
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Consumo(Base):
    __tablename__ = "consumos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(120), nullable=False)
    gasto = Column(Numeric(10,2),nullable=False)
    data = Column(DateTime, server_default=func.now())
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    meta_id = Column(Integer, ForeignKey("metas.id_meta"), nullable=True)
    usuario = relationship("Usuario", back_populates="consumos")
    meta = relationship("Meta", back_populates="consumos")

