from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import mapped_column, relationship

from src.adapters.database.database_settings import Base
from src.ports.enums import Role


class User(Base):
    __tablename__ = "users"

    ID = mapped_column(UUID, primary_key=True, index=True)
    Name = mapped_column(String(15), nullable=True)
    Surname = mapped_column(String(15), nullable=True)
    Phone_number = mapped_column(String(15), nullable=True)
    Email = mapped_column(String, nullable=False)
    Role = mapped_column(
        Enum(Role, name="role_enum", native_enum=False),
        nullable=False,
        default=Role.USER,
    )
    Group_id = mapped_column(UUID, ForeignKey("groups.ID"), nullable=False)
    Image = mapped_column(String, nullable=True)
    IsBlocked = mapped_column(Boolean, nullable=False, default=False)
    Created_at = mapped_column(DateTime, nullable=False, default=func.now())
    Modified_at = mapped_column(DateTime, nullable=True)

    group = relationship("Group", back_populates="user", lazy="select", uselist=False)
