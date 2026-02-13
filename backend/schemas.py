from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- SCHEMAS DE USUARIO (Cobradores/Admin) ---

class UserBase(BaseModel):
    username: str
    nombre: str
    role: str
    zona: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None # Opcional para cuando solo actualizamos perfil

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- SCHEMAS DE PAGOS ---

class PagoBase(BaseModel):
    monto: float
    comentario: Optional[str] = None

class PagoCreate(PagoBase):
    cliente_id: int

class PagoResponse(PagoBase):
    id: int
    fecha: datetime
    saldo_anterior: Optional[float]
    cliente_id: int
    class Config:
        from_attributes = True

# --- SCHEMAS DE CLIENTES ---

class ClienteBase(BaseModel):
    nombre: str
    barrio: str
    direccion: str
    telefono: Optional[str] = None
    saldo: float
    interes: float = 0.0
    # --- NUEVOS CAMPOS AGREGADOS ---
    frecuencia: str = "Diario"  # "Diario" o "Semanal"
    cuota_sugerida: float = 0.0

class ClienteCreate(ClienteBase):
    cobrador_id: str  # Recibimos el username del cobrador desde Astro

class ClienteResponse(ClienteBase):
    id: int
    cobrador_id: int
    activo: bool
    fecha_registro: datetime
    # Se incluyen automáticamente frecuencia y cuota_sugerida por heredar de ClienteBase

    class Config:
        from_attributes = True

# --- SCHEMA DE LOGIN ---

class LoginRequest(BaseModel):
    username: str
    password: str