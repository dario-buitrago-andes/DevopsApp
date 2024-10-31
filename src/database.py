# src/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Obtén la ruta actual del script en ejecución
current_dir = os.path.dirname(os.path.abspath(__file__))
print("current_dir ",current_dir)
# Retrocede una carpeta
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
print("parent_dir ",parent_dir)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("DATABASE_URL", DATABASE_URL)

engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(session_factory)

def init_db():
    from .models.model import Blacklist, Base # Adjusted import statement
    Base.metadata.create_all(bind=engine)