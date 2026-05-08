import io
import uuid
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from sqlalchemy.orm import Session

from app.database import get_db
from app.detector import detect_face
from app.drawer import draw_roi
from app.crud import save_roi, get_rois_by_session, get_latest_roi
from app.schemas import ROIRecordCreate, ROIRecordOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real-Time Face Detection API",
    description="Accepts video frames, detects faces, draws ROI using Pillow, stores in PostgreSQL.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# ENDPOINT 1 — Health Check
# ─────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ─────────────────────────────────────────
# ENDPOINT 2 — WebSocket: Receive + Serve Video Feed
# ─────────────────────────────────────────
@app.websocket("/ws/stream")
async def video_stream(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    # Unique ID to group all frames from this connection
    session_id = str(uuid.uuid4())
    logger.info(f"New WebSocket connection — session_id: {session_id}")

    # Send session_id to frontend as first message
    await websocket.send_json({"type": "session", "session_id": session_id})

    try:
        frame_count = 0

        while True:
            # Receive raw JPEG bytes from frontend
            raw_bytes = await websocket.receive_bytes()

            # Convert bytes to PIL Image
            try:
                image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            except Exception as e:
                logger.warning(f"Could not decode frame: {e}")
                continue

            frame_id = f"{session_id}_{frame_count}"
            frame_count += 1

            # Run face detection
            detection = detect_face(image)

            if detection:
                x, y, w, h, confidence = detection

                # Draw bounding box using Pillow
                annotated_image = draw_roi(image, x, y, w, h, confidence)

                # Save ROI to database
                roi_data = ROIRecordCreate(
                    session_id=session_id,
                    frame_id=frame_id,
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    confidence=confidence,
                )
                save_roi(db, roi_data)
                logger.info(f"Face detected — frame: {frame_id} | box: ({x},{y},{w},{h}) | conf: {confidence:.2f}")

            else:
                annotated_image = image
                logger.debug(f"No face detected — frame: {frame_id}")

            # Encode annotated image back to JPEG bytes
            buffer = io.BytesIO()
            annotated_image.save(buffer, format="JPEG", quality=85)
            annotated_bytes = buffer.getvalue()

            # Send annotated frame back to frontend
            await websocket.send_bytes(annotated_bytes)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected — session_id: {session_id}")

    except Exception as e:
        logger.error(f"Unexpected error in WebSocket handler: {e}")
        await websocket.close(code=1011)


# ─────────────────────────────────────────
# ENDPOINT 3 — GET: Serve ROI Data
# ─────────────────────────────────────────
@app.get("/roi", response_model=list[ROIRecordOut])
def get_roi_data(
    session_id: str = Query(..., description="Session ID"),
    limit: int = Query(50, ge=1, le=500, description="Max number of records to return"),
    db: Session = Depends(get_db),
):
    records = get_rois_by_session(db, session_id)
    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No ROI records found for session_id: {session_id}"
        )
    return records[:limit]


# ─────────────────────────────────────────
# ENDPOINT 4 — GET: Latest ROI only
# ─────────────────────────────────────────
@app.get("/roi/latest", response_model=ROIRecordOut)
def get_latest_roi_data(
    session_id: str = Query(..., description="Session ID"),
    db: Session = Depends(get_db),
):
    record = get_latest_roi(db, session_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No ROI records found for session_id: {session_id}"
        )
    return record