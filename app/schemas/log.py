from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class HabitLogCreate(BaseModel):
    completed: bool = True
    notes: Optional[str] = Field(default=None, max_length=500, description="Optional friction notes or reflections")


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    completed: bool
    notes: Optional[str] = None
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)