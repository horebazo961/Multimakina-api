from sqlalchemy import Column, Integer, String, Boolean
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True} # Previene conflictos de recarga

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="TECNICO")
    is_active = Column(Boolean, default=True)