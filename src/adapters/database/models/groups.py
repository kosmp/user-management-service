from sqlalchemy import UUID, DateTime, String, func, Index, text
from sqlalchemy.orm import mapped_column, relationship

from src.adapters.database.models.users import Base


class Group(Base):
    __tablename__ = "groups"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = mapped_column(String(15), nullable=False, unique=True)
    created_at = mapped_column(DateTime, nullable=False, default=func.now())

    users = relationship(
        "User",
        back_populates="group",
        lazy="dynamic",
        uselist=True,
    )


Index("idx_unique_name", Group.name, unique=True)
