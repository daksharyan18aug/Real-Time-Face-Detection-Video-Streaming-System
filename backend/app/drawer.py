from PIL import Image, ImageDraw, ImageFont


def draw_roi(
    image: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    confidence: float | None = None
) -> Image.Image:
    """
    Draws an axis-aligned bounding box (ROI) on a PIL Image.
    Uses Pillow only — no OpenCV.
    Returns a new annotated image.
    """
    # Work on a copy — never mutate the original
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    # Draw the bounding box rectangle
    draw.rectangle(
        [x, y, x + w, y + h],
        outline=(0, 255, 0),  # green
        width=3
    )

    # Draw confidence label above the box
    if confidence is not None:
        label = f"Face: {confidence:.0%}"

        # Draw label background
        draw.rectangle(
            [x, y - 20, x + 110, y],
            fill=(0, 255, 0)
        )

        # Draw label text
        draw.text(
            (x + 4, y - 18),
            label,
            fill=(0, 0, 0)
        )

    return annotated