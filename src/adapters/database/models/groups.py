from sqlalchemy import UUID, DateTime, String, func, Index
from sqlalchemy.orm import mapped_column, relationship

from src.adapters.database.database_settings import Base


class Group(Base):
    __tablename__ = "groups"

    id = mapped_column(UUID, primary_key=True, index=True)
    name = mapped_column(String(15), nullable=False, unique=True)
    created_at = mapped_column(DateTime, nullable=False, default=func.now())

    users = relationship("User", back_populates="group", lazy="joined", uselist=True)


Index("idx_unique_name", Group.name, unique=True)
