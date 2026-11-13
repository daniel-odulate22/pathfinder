"""On-demand text reading for Pathfinder using RapidOCR, a scene-text model.

It replaced Tesseract, which missed most real signs in testing (see DEVLOG).
Results can still be wrong; treat them as a hint, never as verified information.
"""

import re

MAX_WORDS = 30
_engine = None


def format_reading(lines, min_confidence=0.6):
    """Turn (text, confidence) lines into one spoken answer."""
    # The voice is English, so skip lines with no Latin letters or digits.
    kept = [
        text.strip() for text, confidence in lines
        if confidence >= min_confidence and re.search(r"[A-Za-z0-9]", text)
    ]
    words = ", ".join(kept).split()[:MAX_WORDS]
    if not words:
        return "I cannot read any text right now."
    return "The text reads: " + " ".join(words).rstrip(",")


def read_text(frame):
    """Return a spoken answer describing text found in a BGR camera frame."""
    global _engine
    try:
        if _engine is None:
            from rapidocr_onnxruntime import RapidOCR  # slow import, loaded on first use
            _engine = RapidOCR()
        result, _ = _engine(frame)
    except Exception as exc:
        print(f"Text reading failed: {exc}")
        return "Text reading is not available right now."
    return format_reading([(line[1], float(line[2])) for line in result or []])
