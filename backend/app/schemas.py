from pydantic import BaseModel
from datetime import datetime


class ROIRecordBase(BaseModel):
    session_id: str
    frame_id:   str
    x:          int
    y:          int
    width:      int
    height:     int
    confidence: float | None = None


class ROIRecordCreate(ROIRecordBase):
    pass


class ROIRecordOut(ROIRecordBase):
    id:        int
    timestamp: datetime

    class Config:
        from_attributes = True