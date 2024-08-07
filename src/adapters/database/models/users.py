from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    func,
    text,
)
from sqlalchemy.orm import mapped_column, relationship, DeclarativeBase
from src.ports.enums import Role


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = mapped_column(String(15), nullable=True)
    surname = mapped_column(String(15), nullable=True)
    username = mapped_column(String, nullable=False, unique=True)
    phone_number = mapped_column(String(15), nullable=False, unique=True)
    email = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)
    role = mapped_column(
        Enum(Role, name="role_enum", native_enum=False),
        nullable=False,
        default=Role.USER,
    )
    group_id = mapped_column(
        UUID, ForeignKey("groups.id", ondelete="RESTRICT"), nullable=False
    )
    image = mapped_column(String, nullable=True)
    is_blocked = mapped_column(Boolean, nullable=False, default=False)
    created_at = mapped_column(DateTime, nullable=False, default=func.now())
    modified_at = mapped_column(
        DateTime, nullable=True, onupdate=func.current_timestamp()
    )

    group = relationship("Group", back_populates="users", lazy="joined", uselist=False)
