
# Simplified ORM Models for J.A.R.V.I.S.

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)    
    role_id = Column(Integer, ForeignKey('roles.id'))    
    role = relationship("Role", back_populates="users")