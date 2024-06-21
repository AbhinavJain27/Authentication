from sqlalchemy import Column, String, Integer
from database import Base

class Users(Base):
    __tablename__="users"
    id=Column(Integer , primary_key=True , index=True)
    username=Column(String(50), nullable=False, unique=True)
    hashed_password=Column(String(100), nullable=False)