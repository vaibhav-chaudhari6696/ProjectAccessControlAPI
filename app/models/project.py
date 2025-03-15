from typing import Optional
from sqlmodel import Field, Relationship
from .base import BaseModel
from .user import User

class Project(BaseModel, table=True):
    name: str = Field(index=True)
    description: str
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Relationships
    created_by: Optional[User] = Relationship(back_populates="projects")

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    created_by_id: int 