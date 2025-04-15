from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

if os.getenv("RUNNING_IN_DOCKER"):
    DATABASE_URL = "postgresql://myuser:mypassword@postgres:5432/mydb"
else:
    DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydb" 

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()