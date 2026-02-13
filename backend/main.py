import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

# Importaciones de tus archivos locales
import models, database, auth, schemas
from seed import create_admin  # Asegúrate de tener el archivo seed.py en la raíz

# Inicializar tablas en la base de datos
# Render ejecutará esto cada vez que inicie el servicio
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="CobroDigital API - Producción")

# --- EVENTO DE INICIO (STARTUP) ---
# Se ejecuta automáticamente cada vez que el servidor arranca en Render
@app.on_event("startup")
def on_startup():
    print("🚀 Iniciando servidor y verificando Admin...")
    try:
        create_admin()
        print("✅ Proceso de seed finalizado.")
    except Exception as e:
        print(f"❌ Error al ejecutar la seed: {e}")

# --- CONFIGURACIÓN DE CORS ---
# Obtenemos la URL de Vercel de las variables de entorno
VERCEL_URL = os.getenv("VERCEL_URL", "https://cobrodigitalweb.vercel.app")

origins = [
    VERCEL_URL,
    "https://cobrodigitalweb.vercel.app", # Agregada explícitamente sin "/"
    "http://localhost:4321",
    "http://127.0.0.1:4321"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # O puedes usar ["*"] si quieres evitar problemas para siempre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online", 
        "message": "API de CobroDigital operativa en Render",
        "environment": "production" if os.getenv("RENDER") else "local"
    }

# --- SECCIÓN: AUTH & PERFIL ---

@app.post("/login")
def login(payload: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    return {
        "id": user.username,
        "nombre": user.nombre,
        "role": user.role,
        "zona": user.zona
    }

@app.put("/cobradores/{username}")
def actualizar_perfil_cobrador(username: str, data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Cobrador no encontrado")

    user.nombre = data.nombre
    user.zona = data.zona
    if data.password:
        user.hashed_password = auth.get_password_hash(data.password)

    db.commit()
    return {"message": "Perfil actualizado", "nombre": user.nombre}

# --- SECCIÓN: COBRADORES ---

@app.get("/cobradores", response_model=List[schemas.UserResponse])
def get_cobradores(db: Session = Depends(database.get_db)):
    return db.query(models.User).filter(models.User.role == "cobrador").all()

@app.post("/cobradores")
def crear_cobrador(data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    nuevo_cobrador = models.User(
        username=data.username,
        hashed_password=auth.get_password_hash(data.password),
        nombre=data.nombre,
        role="cobrador",
        zona=data.zona
    )
    db.add(nuevo_cobrador)
    db.commit()
    return {"message": "Cobrador creado con éxito"}

# --- SECCIÓN: CLIENTES ---

@app.get("/clientes", response_model=List[schemas.ClienteResponse])
def get_clientes(cobrador_id: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Cliente)
    if cobrador_id:
        user = db.query(models.User).filter(models.User.username == cobrador_id).first()
        if user:
            query = query.filter(models.Cliente.cobrador_id == user.id)
    return query.all()

@app.post("/clientes")
def crear_cliente(data: schemas.ClienteCreate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == data.cobrador_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Cobrador no encontrado")

    nuevo_cliente = models.Cliente(
        nombre=data.nombre,
        barrio=data.barrio,
        direccion=data.direccion,
        telefono=data.telefono,
        saldo=data.saldo,
        interes=data.interes,
        frecuencia=data.frecuencia,
        cuota_sugerida=data.cuota_sugerida,
        cobrador_id=user.id,
        activo=True
    )
    db.add(nuevo_cliente)
    db.commit()
    return {"message": "Cliente registrado con éxito"}

@app.put("/clientes/{cliente_id}/nueva-deuda")
def asignar_nueva_deuda(cliente_id: int, data: schemas.ClienteCreate, db: Session = Depends(database.get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cliente.saldo = data.saldo
    cliente.interes = data.interes
    cliente.cuota_sugerida = data.cuota_sugerida
    cliente.frecuencia = data.frecuencia
    cliente.activo = True 
    cliente.direccion = data.direccion
    cliente.telefono = data.telefono

    db.commit()
    return {"message": "Nueva deuda asignada", "nuevo_saldo": cliente.saldo}

# --- SECCIÓN: PAGOS ---

@app.post("/pagar", response_model=schemas.PagoResponse)
def registrar_pago(data: schemas.PagoCreate, db: Session = Depends(database.get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    saldo_antes = cliente.saldo
    cliente.saldo -= data.monto
    
    if cliente.saldo <= 0:
        cliente.saldo = 0
        cliente.activo = False

    nuevo_pago = models.Pago(
        monto=data.monto,
        saldo_anterior=saldo_antes,
        commentario=data.comentario,
        cliente_id=data.cliente_id,
        fecha=datetime.utcnow()
    )
    
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

@app.get("/pagos/{cliente_id}", response_model=List[schemas.PagoResponse])
def obtener_historial_pagos(cliente_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Pago).filter(models.Pago.cliente_id == cliente_id).all()

@app.delete("/pagos/{pago_id}")
def eliminar_pago(pago_id: int, db: Session = Depends(database.get_db)):
    pago = db.query(models.Pago).filter(models.Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    cliente = db.query(models.Cliente).filter(models.Cliente.id == pago.cliente_id).first()
    if cliente:
        cliente.saldo += pago.monto
        if not cliente.activo:
            cliente.activo = True

    db.delete(pago)
    db.commit()
    return {"message": "Pago eliminado. El saldo ha sido restaurado correctamente."}