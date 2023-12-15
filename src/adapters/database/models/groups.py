from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.adapters.database.database_settings import Base


class Group(Base):
    __tablename__ = "groups"

    ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    Created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="group", lazy="joined")
