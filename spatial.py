"""Image-space context helpers for Pathfinder.

These heuristics describe visual position and prominence in a camera frame.
They do not estimate physical distance, collision probability, or safe routes.
"""


def get_horizontal_position(x1, x2, frame_width):
    """Classify an object's bounding-box centre within the camera frame."""
    if frame_width <= 0:
        raise ValueError("frame_width must be greater than zero")

    center_x = (x1 + x2) / 2
    relative_x = center_x / frame_width

    if relative_x < 1 / 3:
        return "LEFT"
    if relative_x > 2 / 3:
        return "RIGHT"
    return "CENTRE"


def get_visual_prominence(x1, y1, x2, y2, frame_width, frame_height):
    """Estimate how much of the image frame a detection occupies."""
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("Frame dimensions must be greater than zero")

    box_width = max(0, min(x2, frame_width) - max(x1, 0))
    box_height = max(0, min(y2, frame_height) - max(y1, 0))
    frame_area = frame_width * frame_height
    area_ratio = (box_width * box_height) / frame_area

    return area_ratio


def get_attention_level(position, area_ratio):
    """Return a visual-attention heuristic, not a safety or danger rating."""
    if position == "CENTRE" and area_ratio >= 0.08:
        return "HIGH"
    if area_ratio >= 0.18:
        return "HIGH"
    if position == "CENTRE" or area_ratio >= 0.05:
        return "MEDIUM"
    return "LOW"


def get_detection_context(box, frame_width, frame_height):
    """Return image-space position, prominence, and attention level."""
    x1, y1, x2, y2 = box
    position = get_horizontal_position(x1, x2, frame_width)
    area_ratio = get_visual_prominence(
        x1, y1, x2, y2, frame_width, frame_height
    )
    attention = get_attention_level(position, area_ratio)

    return {
        "position": position,
        "area_ratio": area_ratio,
        "attention": attention,
    }
