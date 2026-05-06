from sqlalchemy.orm import Session
from app.models import ROIRecord
from app.schemas import ROIRecordCreate


def save_roi(db: Session, roi: ROIRecordCreate) -> ROIRecord:
    """Save a new ROI record to the database."""
    record = ROIRecord(
        session_id = roi.session_id,
        frame_id   = roi.frame_id,
        x          = roi.x,
        y          = roi.y,
        width      = roi.width,
        height     = roi.height,
        confidence = roi.confidence,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_rois_by_session(db: Session, session_id: str) -> list[ROIRecord]:
    """Fetch all ROI records for a given session."""
    return (
        db.query(ROIRecord)
        .filter(ROIRecord.session_id == session_id)
        .order_by(ROIRecord.timestamp.desc())
        .all()
    )


def get_latest_roi(db: Session, session_id: str) -> ROIRecord | None:
    """Fetch the most recent ROI record for a session."""
    return (
        db.query(ROIRecord)
        .filter(ROIRecord.session_id == session_id)
        .order_by(ROIRecord.timestamp.desc())
        .first()
    )