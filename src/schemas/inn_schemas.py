import enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InnStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class InnResultBase(BaseModel):
    """
    Общие поля для всех схем.
    """
    task_id: str = Field(..., )
    inn: str = Field(
        ..., min_length=10, max_length=12,
        description="ИНН организации или ИП",
    )
    status: InnStatus = Field(..., description="Текущий статус задачи")

class InnResultCreate(BaseModel):
    inn: str = Field(..., min_length=10, max_length=12)

class InnResultResponse(InnResultBase):
    data: dict | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)