import pytest
from PIL import Image
from app.detector import detect_face


def test_detect_face_returns_none_on_blank_image():
    """A blank image should return None — no face present."""
    blank = Image.new("RGB", (640, 480), color=(200, 200, 200))
    result = detect_face(blank)
    assert result is None


def test_detect_face_returns_tuple_on_face_image():
    """
    A real face image should return a 5-tuple.
    Download any face image and save as tests/face.jpg to enable this.
    """
    import os
    face_path = os.path.join(os.path.dirname(__file__), "face.jpg")
    if not os.path.exists(face_path):
        pytest.skip("No test face image found — add tests/face.jpg to enable")

    image = Image.open(face_path)
    result = detect_face(image)
    assert result is not None
    assert len(result) == 5
    x, y, w, h, conf = result
    assert w > 0 and h > 0
    assert 0.0 <= conf <= 1.0