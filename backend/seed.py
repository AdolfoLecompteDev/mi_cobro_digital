from database import SessionLocal
from models import User
from auth import get_password_hash

def create_admin():
    db = SessionLocal()
    # Verificamos si ya existe
    user_exists = db.query(User).filter(User.username == "admin").first()
    
    if not user_exists:
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin123"), # Esta será tu clave
            role="admin",
            nombre="Administrador Principal",
            zona="General"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Usuario Admin creado: user: admin | pass: admin123")
    else:
        print("ℹ️ El admin ya existe.")
    db.close()

if __name__ == "__main__":
    create_admin()