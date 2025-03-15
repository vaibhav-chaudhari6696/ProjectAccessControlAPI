from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(BaseModel, table=True):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="created_by")

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    role: Optional[UserRole] = UserRole.USER

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool 