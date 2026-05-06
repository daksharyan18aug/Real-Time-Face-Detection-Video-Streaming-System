import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import urllib.request
import os

# Path to store the model file
MODEL_PATH = os.path.join(os.path.dirname(__file__), "blaze_face_short_range.tflite")

def _ensure_model():
    """Download the face detection model if not present."""
    if not os.path.exists(MODEL_PATH):
        url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
        print(f"Downloading face detection model...")
        urllib.request.urlretrieve(url, MODEL_PATH)
        print(f"Model downloaded to {MODEL_PATH}")


def detect_face(image: Image.Image) -> tuple | None:
    """
    Detects a single face in a PIL Image using MediaPipe Tasks API.
    Returns (x, y, width, height, confidence) or None if no face found.
    """
    _ensure_model()

    rgb_array = np.array(image.convert("RGB"))
    ih, iw = rgb_array.shape[:2]

    BaseOptions = mp_python.BaseOptions
    FaceDetector = mp_vision.FaceDetector
    FaceDetectorOptions = mp_vision.FaceDetectorOptions
    VisionRunningMode = mp_vision.RunningMode

    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        min_detection_confidence=0.5,
    )

    with FaceDetector.create_from_options(options) as detector:
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_array
        )
        result = detector.detect(mp_image)

        if not result.detections:
            return None

        # Only one face assumed per task requirement
        det = result.detections[0]
        bbox = det.bounding_box
        confidence = det.categories[0].score

        # Clamp to image boundaries
        x = max(0, bbox.origin_x)
        y = max(0, bbox.origin_y)
        w = min(bbox.width, iw - x)
        h = min(bbox.height, ih - y)

        return x, y, w, h, float(confidence)