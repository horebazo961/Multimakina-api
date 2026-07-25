from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ruta de la base de datos SQLite en la raíz del proyecto
SQLALCHEMY_DATABASE_URL = "sqlite:///./multimakina.db"

# check_same_thread=False es necesario exclusivamente para SQLite en entornos multihilo como FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Generador de sesión de base de datos para inyección de dependencias en FastAPI.
    Garantiza el cierre seguro de la conexión bajo cualquier circunstancia (try/finally).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()