from sqlalchemy import Column, Integer, String, Text, Enum
from database import Base
import enum

class Role(str, enum.Enum):
    ADMIN = "admin"
    AUTHOR = "author"
    READER = "reader"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    role = Column(Enum(Role), default=Role.READER)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    author_id = Column(Integer)