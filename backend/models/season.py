from sqlalchemy import (
    Column,DateTime,
    Boolean,Integer,String, 
    ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Season(Base):
    __tablename__ = "seasons"


    id = Column(Integer, primary_key = True, index = True)
    label = Column(String(16),nullable = False, unique = True, index = True) # "2025/26"
    start_date = Column(DateTime(timezone = True), nullable = True)
    end_date = Column(DateTime(timezone = True), nullable = True)
    is_current = Column(Boolean, default = False)
    #relationships
    standings = relationship("Standing", back_populates = "season")
    # ForeignKey needs "table.column", not the column name on its own -
    # "competition_id" isn't a table, "competitions" is
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable = False, index = True)
    competition = relationship("Competition", back_populates = "seasons")
    fixtures = relationship("Fixture", back_populates = "season")
    player_statistics = relationship("PlayerStatistic", back_populates = "season")
    team_statistics = relationship("TeamStatistic",back_populates="season")

    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
