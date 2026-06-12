from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional
from database import engine, get_db, Base
import models
import schemas

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MECHAAP API", description="API para gestión de canchas de tejo", version="1.0.0")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ENDPOINTS DE AUTENTICACIÓN ==========
@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión - POST /api/auth/login"""
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == login_data.email,
        models.Usuario.contrasena == login_data.contrasena
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "success": True,
        "user_id": usuario.id_usuario,
        "nombre": f"{usuario.nombre} {usuario.apellido}",
        "tipo_usuario": usuario.tipo_usuario,
        "message": "Inicio de sesión exitoso"
    }

@app.post("/api/auth/register", response_model=schemas.UsuarioResponse)
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario - POST /api/auth/register"""
    # Verificar si el email ya existe
    existe = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear nuevo usuario
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        contrasena=usuario.contrasena,
        fecha_registro=date.today(),
        fecha_nacimiento=usuario.fecha_nacimiento,
        direccion=usuario.direccion,
        telefono=usuario.telefono,
        tipo_usuario=usuario.tipo_usuario
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

# ========== ENDPOINTS DE USUARIOS (CRUD COMPLETO) ==========
@app.get("/api/usuarios", response_model=List[schemas.UsuarioResponse])
def get_usuarios(db: Session = Depends(get_db)):
    """Listar todos los usuarios - GET /api/usuarios"""
    usuarios = db.query(models.Usuario).all()
    return usuarios

@app.get("/api/usuarios/{user_id}", response_model=schemas.UsuarioResponse)
def get_usuario(user_id: int, db: Session = Depends(get_db)):
    """Obtener usuario por ID - GET /api/usuarios/{id}"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.put("/api/usuarios/{user_id}")
def update_usuario(user_id: int, usuario_data: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    """Actualizar usuario - PUT /api/usuarios/{id}"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar solo los campos proporcionados
    update_data = usuario_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    return {"success": True, "message": "Usuario actualizado", "usuario": usuario}

@app.delete("/api/usuarios/{user_id}")
def delete_usuario(user_id: int, db: Session = Depends(get_db)):
    """Eliminar usuario - DELETE /api/usuarios/{id}"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"success": True, "message": "Usuario eliminado"}

# ========== ENDPOINTS DE CANCHAS (CRUD COMPLETO) ==========
@app.get("/api/canchas", response_model=List[schemas.CanchaResponse])
def get_canchas(db: Session = Depends(get_db)):
    """Listar todas las canchas - GET /api/canchas"""
    canchas = db.query(models.Cancha).all()
    return canchas

@app.get("/api/canchas/{cancha_id}", response_model=schemas.CanchaDetailResponse)
def get_cancha(cancha_id: int, db: Session = Depends(get_db)):
    """Obtener cancha por ID - GET /api/canchas/{id}"""
    cancha = db.query(models.Cancha).filter(models.Cancha.id_cancha == cancha_id).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    return {
        "id_cancha": cancha.id_cancha,
        "nombre": cancha.nombre,
        "descripcion": cancha.descripcion,
        "capacidad": cancha.capacidad,
        "tipo_cancha": cancha.tipo_cancha,
        "precio": float(cancha.precio),
        "id_usuario_propietario": cancha.id_usuario_propietario,
        "id_ubicacion": cancha.id_ubicacion,
        "propietario_nombre": cancha.propietario.nombre if cancha.propietario else None,
        "ubicacion_ciudad": cancha.ubicacion.ciudad if cancha.ubicacion else None
    }

@app.post("/api/canchas", response_model=schemas.CanchaResponse)
def create_cancha(cancha: schemas.CanchaCreate, db: Session = Depends(get_db)):
    """Crear nueva cancha - POST /api/canchas"""
    nueva_cancha = models.Cancha(**cancha.dict())
    db.add(nueva_cancha)
    db.commit()
    db.refresh(nueva_cancha)
    return nueva_cancha

@app.put("/api/canchas/{cancha_id}")
def update_cancha(cancha_id: int, cancha_data: schemas.CanchaBase, db: Session = Depends(get_db)):
    """Actualizar cancha - PUT /api/canchas/{id}"""
    cancha = db.query(models.Cancha).filter(models.Cancha.id_cancha == cancha_id).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    for key, value in cancha_data.dict().items():
        setattr(cancha, key, value)
    
    db.commit()
    db.refresh(cancha)
    return {"success": True, "message": "Cancha actualizada"}

@app.delete("/api/canchas/{cancha_id}")
def delete_cancha(cancha_id: int, db: Session = Depends(get_db)):
    """Eliminar cancha - DELETE /api/canchas/{id}"""
    cancha = db.query(models.Cancha).filter(models.Cancha.id_cancha == cancha_id).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    db.delete(cancha)
    db.commit()
    return {"success": True, "message": "Cancha eliminada"}

# ========== ENDPOINTS DE RESERVAS (CRUD COMPLETO) ==========
@app.get("/api/reservas", response_model=List[schemas.ReservaResponse])
def get_reservas(db: Session = Depends(get_db)):
    """Listar todas las reservas - GET /api/reservas"""
    reservas = db.query(models.Reserva).all()
    return [
        {
            "id_reserva": r.id_reserva,
            "fecha": r.fecha,
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "estado": r.estado,
            "id_usuario": r.id_usuario,
            "id_cancha": r.id_cancha,
            "nombre_cancha": r.cancha.nombre if r.cancha else None
        }
        for r in reservas
    ]

@app.get("/api/reservas/usuario/{usuario_id}", response_model=List[schemas.ReservaResponse])
def get_reservas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener reservas de un usuario - GET /api/reservas/usuario/{id}"""
    reservas = db.query(models.Reserva).filter(models.Reserva.id_usuario == usuario_id).all()
    return [
        {
            "id_reserva": r.id_reserva,
            "fecha": r.fecha,
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "estado": r.estado,
            "id_usuario": r.id_usuario,
            "id_cancha": r.id_cancha,
            "nombre_cancha": r.cancha.nombre if r.cancha else None
        }
        for r in reservas
    ]

@app.post("/api/reservas", response_model=schemas.ReservaResponse)
def create_reserva(reserva: schemas.ReservaCreate, db: Session = Depends(get_db)):
    """Crear nueva reserva - POST /api/reservas"""
    # Verificar si la cancha existe
    cancha = db.query(models.Cancha).filter(models.Cancha.id_cancha == reserva.id_cancha).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    # Convertir horas a formato time
    hora_inicio_time = datetime.strptime(reserva.hora_inicio, "%H:%M").time()
    hora_fin_time = datetime.strptime(reserva.hora_fin, "%H:%M").time()
    
    # Verificar disponibilidad
    conflicto = db.query(models.Reserva).filter(
        models.Reserva.id_cancha == reserva.id_cancha,
        models.Reserva.fecha == reserva.fecha,
        models.Reserva.estado.in_(["pendiente", "confirmado"]),
        models.Reserva.hora_inicio < hora_fin_time,
        models.Reserva.hora_fin > hora_inicio_time
    ).first()
    
    if conflicto:
        raise HTTPException(status_code=400, detail="La cancha no está disponible en ese horario")
    
    nueva_reserva = models.Reserva(
        fecha=reserva.fecha,
        hora_inicio=hora_inicio_time,
        hora_fin=hora_fin_time,
        estado="pendiente",
        id_usuario=reserva.id_usuario,
        id_cancha=reserva.id_cancha
    )
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    
    return {
        "id_reserva": nueva_reserva.id_reserva,
        "fecha": nueva_reserva.fecha,
        "hora_inicio": str(nueva_reserva.hora_inicio),
        "hora_fin": str(nueva_reserva.hora_fin),
        "estado": nueva_reserva.estado,
        "id_usuario": nueva_reserva.id_usuario,
        "id_cancha": nueva_reserva.id_cancha,
        "nombre_cancha": cancha.nombre
    }

@app.put("/api/reservas/{reserva_id}/estado")
def update_reserva_estado(reserva_id: int, estado: str, db: Session = Depends(get_db)):
    """Actualizar estado de reserva - PUT /api/reservas/{id}/estado"""
    reserva = db.query(models.Reserva).filter(models.Reserva.id_reserva == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    if estado not in ["pendiente", "confirmado", "cancelado", "completado"]:
        raise HTTPException(status_code=400, detail="Estado no válido")
    
    reserva.estado = estado
    db.commit()
    
    return {"success": True, "message": f"Reserva {estado}"}

@app.delete("/api/reservas/{reserva_id}")
def delete_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Eliminar reserva - DELETE /api/reservas/{id}"""
    reserva = db.query(models.Reserva).filter(models.Reserva.id_reserva == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    db.delete(reserva)
    db.commit()
    return {"success": True, "message": "Reserva eliminada"}

# ========== ENDPOINTS DE TORNEOS ==========
@app.get("/api/torneos", response_model=List[schemas.TorneoResponse])
def get_torneos(db: Session = Depends(get_db)):
    """Listar todos los torneos - GET /api/torneos"""
    torneos = db.query(models.Torneo).all()
    return torneos

@app.get("/api/torneos/activos", response_model=List[schemas.TorneoResponse])
def get_torneos_activos(db: Session = Depends(get_db)):
    """Listar torneos activos - GET /api/torneos/activos"""
    torneos = db.query(models.Torneo).filter(models.Torneo.estado == True).all()
    return torneos

@app.post("/api/torneos", response_model=schemas.TorneoResponse)
def create_torneo(torneo: schemas.TorneoCreate, db: Session = Depends(get_db)):
    """Crear nuevo torneo - POST /api/torneos"""
    nuevo_torneo = models.Torneo(**torneo.dict())
    db.add(nuevo_torneo)
    db.commit()
    db.refresh(nuevo_torneo)
    return nuevo_torneo

@app.post("/api/torneos/{torneo_id}/inscribir")
def inscribir_torneo(torneo_id: int, usuario_id: int, db: Session = Depends(get_db)):
    """Inscribir usuario a torneo - POST /api/torneos/{id}/inscribir"""
    # Verificar si el torneo existe
    torneo = db.query(models.Torneo).filter(models.Torneo.id_torneo == torneo_id).first()
    if not torneo:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")
    
    # Verificar si ya está inscrito
    existe = db.query(models.Inscripcion).filter(
        models.Inscripcion.id_torneo == torneo_id,
        models.Inscripcion.id_usuario == usuario_id
    ).first()
    
    if existe:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este torneo")
    
    inscripcion = models.Inscripcion(
        fecha_inscripcion=date.today(),
        estado="pendiente",
        id_usuario=usuario_id,
        id_torneo=torneo_id
    )
    
    db.add(inscripcion)
    db.commit()
    
    return {"success": True, "message": "Inscripción exitosa"}

# ========== ENDPOINTS DE ESTADÍSTICAS ==========
@app.get("/api/stats/usuarios")
def count_usuarios(db: Session = Depends(get_db)):
    total = db.query(models.Usuario).count()
    return {"total": total}

@app.get("/api/stats/canchas")
def count_canchas(db: Session = Depends(get_db)):
    total = db.query(models.Cancha).count()
    return {"total": total}

@app.get("/api/stats/reservas")
def count_reservas(db: Session = Depends(get_db)):
    total = db.query(models.Reserva).count()
    activas = db.query(models.Reserva).filter(models.Reserva.estado == "confirmado").count()
    return {"total": total, "activas": activas}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API MECHAAP funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)