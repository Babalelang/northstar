from sqlalchemy import(
     Column,
     DateTime,
     Enum,
     Text,
     Boolean,
     Integer,
     String, ForeignKey)
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.sql import func
from database.database import Base

class AnnouncementStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class AnnouncementType(str,enum.Enum):
    TRANSFER = "transfer"
    GENERAL = "general"
    MATCH = "match"
    WEATHER = "weather"

class Announcement(Base):
    __tablename__ = "announcements"


    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(200), nullable = False)
    slug = Column(String(220),nullable = False, unique=True, index=True)
    summary = Column(String(330),nullable = True)
    body = Column(Text, nullable = False)
    status = Column(Enum(AnnouncementStatus), nullable = False, default = AnnouncementStatus.DRAFT, index = True)
    author_id = Column(Integer,ForeignKey("users.id"), nullable = False)
    announcement_type = Column(Enum(AnnouncementType), nullable = False, default = AnnouncementType.GENERAL, index = True)
    published_at = Column(DateTime(timezone = True), nullable = True)
    featured_image_url = Column(String(255),nullable = True)
    is_pinned = Column(Boolean, default = False, nullable = False)
    #relationships
    author = relationship("User", back_populates = "announcements")

    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
    deleted_at = Column(
    DateTime(timezone=True),
    nullable=True,
)