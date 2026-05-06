import numpy as np
import mediapipe as mp
from PIL import Image


def detect_face(image: Image.Image) -> tuple | None:
    """
    Detects a single face in a PIL Image.
    Returns (x, y, width, height, confidence) or None if no face found.
    """
    mp_face = mp.solutions.face_detection

    rgb_array = np.array(image.convert("RGB"))
    ih, iw = rgb_array.shape[:2]

    with mp_face.FaceDetection(
        model_selection=0,
        min_detection_confidence=0.5
    ) as detector:

        results = detector.process(rgb_array)

        if not results.detections:
            return None

        # Only one face assumed per task requirement
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        confidence = detection.score[0]

        # Convert relative coords to absolute pixel values
        x = int(bbox.xmin * iw)
        y = int(bbox.ymin * ih)
        w = int(bbox.width * iw)
        h = int(bbox.height * ih)

        # Clamp values to image boundaries
        x = max(0, x)
        y = max(0, y)
        w = min(w, iw - x)
        h = min(h, ih - y)

        return x, y, w, h, float(confidence)