from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class TimestampModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class BaseModel(TimestampModel):
    id: Optional[int] = Field(default=None, primary_key=True) 