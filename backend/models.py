from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from datetime import date

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    fecha_registro = Column(Date, default=date.today)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(String(20))
    tipo_usuario = Column(String(20), nullable=False, default="cliente")
    
    # Relaciones
    reservas = relationship("Reserva", back_populates="usuario")
    canchas = relationship("Cancha", foreign_keys="Cancha.id_usuario_propietario")

class Ubicacion(Base):
    __tablename__ = "ubicacion"
    
    id_ubicacion = Column(Integer, primary_key=True, index=True)
    ciudad = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=False)
    latitud = Column(DECIMAL(10,8))
    longitud = Column(DECIMAL(11,8))
    
    canchas = relationship("Cancha", back_populates="ubicacion")

class Cancha(Base):
    __tablename__ = "canchas"
    
    id_cancha = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    capacidad = Column(Integer, nullable=False)
    tipo_cancha = Column(String(50), nullable=False)
    precio = Column(DECIMAL(10,2), nullable=False)
    id_usuario_propietario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_ubicacion = Column(Integer, ForeignKey("ubicacion.id_ubicacion"))
    
    # Relaciones
    propietario = relationship("Usuario", foreign_keys=[id_usuario_propietario])
    ubicacion = relationship("Ubicacion", back_populates="canchas")
    reservas = relationship("Reserva", back_populates="cancha")
    disponibilidad = relationship("Disponibilidad", back_populates="cancha")

class Reserva(Base):
    __tablename__ = "reservas"
    
    id_reserva = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(30), nullable=False, default="pendiente")
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_cancha = Column(Integer, ForeignKey("canchas.id_cancha"))
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="reservas")
    cancha = relationship("Cancha", back_populates="reservas")

class Disponibilidad(Base):
    __tablename__ = "disponibilidad"
    
    id_disponibilidad = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False, default="disponible")
    id_cancha = Column(Integer, ForeignKey("canchas.id_cancha"))
    
    cancha = relationship("Cancha", back_populates="disponibilidad")

class Torneo(Base):
    __tablename__ = "torneos"
    
    id_torneo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    estado = Column(Boolean, nullable=False, default=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    tipo_torneo = Column(String(50))
    tipo_participacion = Column(String(20), nullable=False)
    valor_inscripcion = Column(DECIMAL(10,2))
    nivel = Column(String(50))
    cupos_maximos = Column(Integer, nullable=False)

class Inscripcion(Base):
    __tablename__ = "inscripciones"
    
    id_inscripcion = Column(Integer, primary_key=True, index=True)
    fecha_inscripcion = Column(Date, default=date.today)
    estado = Column(String(30), nullable=False, default="pendiente")
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_torneo = Column(Integer, ForeignKey("torneos.id_torneo"))