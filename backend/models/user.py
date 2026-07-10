from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.EDITOR,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # self-referencing fk, tracks which admin/editor created this user
    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    # remote_side tells sqlalchemy which side of the fk is the "one",
    # otherwise it can't tell the two directions of a self join apart
    created_by = relationship(
        "User",
        remote_side=[id],
    )

    announcements = relationship(
        "Announcement",
        back_populates="author",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
