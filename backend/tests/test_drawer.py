from PIL import Image
from app.drawer import draw_roi


def test_draw_roi_returns_pil_image():
    """draw_roi should return a PIL Image."""
    img = Image.new("RGB", (640, 480), color=(100, 100, 100))
    result = draw_roi(img, x=100, y=100, w=200, h=200)
    assert isinstance(result, Image.Image)


def test_draw_roi_does_not_mutate_original():
    """draw_roi should return a copy, not modify the original."""
    original = Image.new("RGB", (640, 480), color=(100, 100, 100))
    original_pixels = list(original.getdata())
    draw_roi(original, x=100, y=100, w=200, h=200)
    assert list(original.getdata()) == original_pixels


def test_draw_roi_same_size_as_input():
    """Output image must be same dimensions as input."""
    img = Image.new("RGB", (640, 480))
    result = draw_roi(img, x=50, y=50, w=100, h=100)
    assert result.size == img.size


def test_draw_roi_with_confidence_label():
    """Should not crash when confidence is provided."""
    img = Image.new("RGB", (640, 480))
    result = draw_roi(img, x=50, y=50, w=100, h=100, confidence=0.93)
    assert isinstance(result, Image.Image)