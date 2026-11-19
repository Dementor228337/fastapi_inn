from src.core.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Enum,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from src.schemas.inn_schemas import InnStatus

class InnResult(Base):
    __tablename__ = "inn_results"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(36), unique=True, index=True, nullable=False)
    inn = Column(String(12), nullable=False)
    status = Column(Enum(InnStatus), default=InnStatus.PENDING, nullable=False)
    data = Column(JSONB, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )