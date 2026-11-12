"""Basic image-space positioning helpers for Pathfinder."""


def get_horizontal_position(x1, x2, frame_width):
    """Classify an object's horizontal position from its bounding-box centre.

    The result describes where the object appears in the camera frame.
    It does not describe the object's real-world direction or distance.
    """
    if frame_width <= 0:
        raise ValueError("frame_width must be greater than zero")

    center_x = (x1 + x2) / 2
    relative_x = center_x / frame_width

    if relative_x < 1 / 3:
        return "LEFT"
    if relative_x > 2 / 3:
        return "RIGHT"
    return "CENTRE"
