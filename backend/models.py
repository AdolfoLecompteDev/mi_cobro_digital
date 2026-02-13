from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="cobrador") # admin o cobrador
    nombre = Column(String(100))
    zona = Column(String(50))

    # --- CORRECCIÓN AQUÍ ---
    # Antes decía relationship("User"...), debe ser con la clase "Cliente"
    clientes = relationship("Cliente", back_populates="cobrador")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    barrio = Column(String(100))
    direccion = Column(String(255))
    telefono = Column(String(20))
    
    # Finanzas
    saldo = Column(Float, default=0.0)
    interes = Column(Float, default=0.0) 
    
    # Ajustes de flexibilidad
    frecuencia = Column(String(20), default="Diario") 
    cuota_sugerida = Column(Float, default=0.0) 
    
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relación con el Cobrador
    cobrador_id = Column(Integer, ForeignKey("users.id"))
    cobrador = relationship("User", back_populates="clientes")
    
    # Relación con Pagos
    pagos = relationship("Pago", back_populates="cliente", cascade="all, delete-orphan")

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    saldo_anterior = Column(Float)
    comentario = Column(String(255))
    
    # Relación con Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    cliente = relationship("Cliente", back_populates="pagos")