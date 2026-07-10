from sqlalchemy import Column,DateTime,Integer,String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key = True, index = True)

    name = Column(String(100),nullable = False, unique = True, index = True)
    city = Column(String(100))
    country = Column(String(100))
    capacity = Column(Integer)
    address = Column(String(255))
    surface = Column(String(50))
    image_url = Column(String(255))
    #relationships
    teams = relationship("Team", back_populates = "venue",)
    fixtures = relationship("Fixture",back_populates = "venue",)
    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
