import os
from sqlalchemy.orm import Session
from database import sessionLocal
from models import User  # Assure-toi que le modèle User est bien défini dans models.py
from passlib.hash import bcrypt

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

def create_admin():
    db: Session = sessionLocal()
    admin_user = db.query(User).filter(User.username == POSTGRES_USER).first()

    if not admin_user:
        print(f"👤 Création de l'utilisateur admin '{POSTGRES_USER}'...")
        new_user = User(username=POSTGRES_USER, email="admin@example.com", hashed_password=bcrypt.hash(POSTGRES_PASSWORD))
        db.add(new_user)
        db.commit()
        print("✅ Utilisateur admin créé avec succès.")
    else:
        print("✅ L'utilisateur admin existe déjà.")

if __name__ == "__main__":
    create_admin()
