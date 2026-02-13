import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Intentamos obtener la URL de PostgreSQL desde las variables de entorno de Render
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- CORRECCIÓN CRÍTICA PARA RENDER/POSTGRESQL ---
# Si la URL empieza con "postgres://", SQLAlchemy fallará. 
# Debemos cambiarlo manualmente a "postgresql://".
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Respaldo por si olvidas configurar la variable (puedes dejarlo en blanco o usar SQLite local)
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Configuramos el motor de la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Evita errores de "conexión perdida"
    pool_recycle=3600    # Refresca conexiones inactivas
    # Nota: No incluimos pool_size alto para evitar saturar el plan Free de Postgres de Render
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()