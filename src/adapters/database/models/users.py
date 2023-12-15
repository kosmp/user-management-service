from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.adapters.database.database_settings import Base
from src.ports.enums import Role


class User(Base):
    __tablename__ = "users"

    ID = Column(UUID, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    Surname = Column(String, nullable=False)
    Phone_number = Column(String, nullable=False)
    Email = Column(String, nullable=False)
    Role = Column(Enum(Role, name="role_enum", native_enum=False), nullable=False)
    Group_id = Column(Integer, ForeignKey("groups.ID"), nullable=False)
    Image = Column(String, nullable=False)
    IsBlocked = Column(Boolean, nullable=False)
    Created_at = Column(DateTime, nullable=False)
    Modified_at = Column(DateTime, nullable=False)

    group = relationship("Group", back_populates="user", lazy="select", uselist=False)
