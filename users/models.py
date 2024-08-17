from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, ARRAY, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    preferences = Column(ARRAY(String))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    embeddings = relationship("UserEmbeddings", back_populates="user", uselist=False)

class UserEmbeddings(Base):
    __tablename__ = "user_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    embeddings = Column(ARRAY(Float))

    user = relationship("User", back_populates="embeddings")
