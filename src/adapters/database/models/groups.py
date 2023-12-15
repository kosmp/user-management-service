from sqlalchemy import UUID, DateTime, String, func, Index
from sqlalchemy.orm import mapped_column, relationship

from src.adapters.database.database_settings import Base


class Group(Base):
    __tablename__ = "groups"

    ID = mapped_column(UUID, primary_key=True, index=True)
    Name = mapped_column(String(15), nullable=False, unique=True)
    Created_at = mapped_column(DateTime, nullable=False, default=func.now())

    user = relationship("User", back_populates="group", lazy="joined")


Index("idx_unique_name", Group.Name, unique=True)
