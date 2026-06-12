from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from decimal import Decimal

# ========== ESQUEMAS DE USUARIO ==========
class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    direccion: str
    telefono: Optional[str] = None
    tipo_usuario: str = "cliente"

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str]
    direccion: str
    tipo_usuario: str
    fecha_registro: date
    
    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    contrasena: Optional[str] = None

# ========== ESQUEMAS DE CANCHA ==========
class UbicacionBase(BaseModel):
    ciudad: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class CanchaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    capacidad: int
    tipo_cancha: str
    precio: float

class CanchaCreate(CanchaBase):
    id_usuario_propietario: int
    id_ubicacion: int

class CanchaResponse(CanchaBase):
    id_cancha: int
    id_usuario_propietario: int
    id_ubicacion: int
    
    class Config:
        from_attributes = True

class CanchaDetailResponse(CanchaResponse):
    propietario_nombre: Optional[str] = None
    ubicacion_ciudad: Optional[str] = None

# ========== ESQUEMAS DE RESERVA ==========
class ReservaBase(BaseModel):
    fecha: date
    hora_inicio: str
    hora_fin: str

class ReservaCreate(ReservaBase):
    id_usuario: int
    id_cancha: int

class ReservaResponse(ReservaBase):
    id_reserva: int
    estado: str
    id_usuario: int
    id_cancha: int
    nombre_cancha: Optional[str] = None
    
    class Config:
        from_attributes = True

class ReservaUpdate(BaseModel):
    estado: str

# ========== ESQUEMAS DE TORNEO ==========
class TorneoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    tipo_torneo: Optional[str] = None
    tipo_participacion: str
    valor_inscripcion: Optional[float] = None
    nivel: Optional[str] = None
    cupos_maximos: int

class TorneoCreate(TorneoBase):
    estado: bool = True

class TorneoResponse(TorneoBase):
    id_torneo: int
    estado: bool
    
    class Config:
        from_attributes = True

# ========== ESQUEMAS DE AUTENTICACIÓN ==========
class LoginRequest(BaseModel):
    email: str
    contrasena: str

class LoginResponse(BaseModel):
    success: bool
    user_id: int
    nombre: str
    tipo_usuario: str
    message: str