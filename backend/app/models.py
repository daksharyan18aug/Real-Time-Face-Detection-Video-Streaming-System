from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class ROIRecord(Base):
    __tablename__ = "roi_records"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    frame_id   = Column(String, index=True, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow, nullable=False)
    x          = Column(Integer, nullable=False)
    y          = Column(Integer, nullable=False)
    width      = Column(Integer, nullable=False)
    height     = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=True)