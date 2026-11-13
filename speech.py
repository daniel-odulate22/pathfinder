"""Voice narration helpers for Pathfinder."""

import queue
import re
import threading

import pyttsx3


ATTENTION_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def build_scene_description(detections, max_objects=3):
    """Turn current detections into a short, plain-language sentence."""
    candidates = [
        item for item in detections
        if item.get("confidence", 0) >= 0.45
    ]
    candidates.sort(
        key=lambda item: (
            ATTENTION_ORDER.get(item.get("attention", "LOW"), 2),
            -item.get("confidence", 0),
        )
    )

    descriptions = []
    seen = set()

    for item in candidates:
        class_name = item["class_name"]
        position = item["position"].lower()
        location = "in the centre" if position == "centre" else f"on the {position}"
        identity = (class_name, position)

        if identity in seen:
            continue

        seen.add(identity)
        descriptions.append(f"{class_name} {location}")

        if len(descriptions) >= max_objects:
            break

    if not descriptions:
        return ""
    if len(descriptions) == 1:
        return f"I can see {descriptions[0]}."

    return "I can see " + ", ".join(descriptions[:-1]) + (
        f", and {descriptions[-1]}."
    )


def should_announce(
    description,
    previous_description,
    now,
    last_announcement_time,
    min_interval=5.0,
    repeat_interval=12.0,
):
    """Announce changed scenes promptly and repeat stable scenes periodically."""
    if not description:
        return False

    elapsed = now - last_announcement_time

    if description != previous_description:
        return elapsed >= min_interval

    return elapsed >= repeat_interval


QUESTION_POSITIONS = (
    ("left", "LEFT"), ("right", "RIGHT"), ("front", "CENTRE"),
    ("ahead", "CENTRE"), ("centre", "CENTRE"), ("center", "CENTRE"),
)


# Everyday words for class names the detection model uses.
OBJECT_ALIASES = {
    "people": "person", "someone": "person", "anyone": "person",
    "table": "dining table", "phone": "cell phone", "sofa": "couch",
    "plant": "potted plant", "television": "tv", "bag": "backpack",
}


def find_target_class(question, known_classes):
    """Return the detectable class a question names, or None."""
    known = set(known_classes)
    names = {name: name for name in known}
    names.update({a: n for a, n in OBJECT_ALIASES.items() if n in known})
    # Longest first so "hot dog" is not mistaken for "dog".
    for word in sorted(names, key=len, reverse=True):
        if re.search(rf"\b{re.escape(word)}(s|es)?\b", question.lower()):
            return names[word]
    return None


def answer_question(question, detections, known_classes=()):
    """Answer a camera-context question using only the current detections.

    known_classes is every class the model can detect, so a search for an
    absent object gets "I cannot see a chair" instead of an unrelated scene.
    """
    lowered = question.lower()
    target = find_target_class(question, known_classes)
    subject = "anything there"
    if target:
        detections = [d for d in detections if d["class_name"] == target]
        subject = f"a {target}"
    elif known_classes and re.search(r"\b(where|find|locate)\b", lowered):
        return ("I cannot look for that. I can find common objects such as "
                "people, chairs, tables, bottles, cups, laptops, and bags.")
    for word, position in QUESTION_POSITIONS:
        if word in lowered:
            detections = [d for d in detections if d["position"] == position]
            if target:
                subject += " there"
            break
    return build_scene_description(detections) or (
        f"I cannot see {subject} right now."
    )


class VoiceNarrator:
    """Speak asynchronously so text-to-speech does not block camera capture."""

    def __init__(self, rate=175, volume=1.0):
        self._queue = queue.Queue(maxsize=1)
        self._rate = rate
        self._volume = volume
        self._thread = threading.Thread(
            target=self._run,
            name="PathfinderVoice",
            daemon=True,
        )
        self._thread.start()

    def _run(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            engine.setProperty("volume", self._volume)

            while True:
                message = self._queue.get()
                if message is None:
                    break
                engine.say(message)
                engine.runAndWait()

            engine.stop()
        except Exception as exc:
            print(f"Voice narration unavailable: {exc}")

    def speak(self, message):
        """Queue the latest narration, dropping an older pending message."""
        if not message:
            return
        try:
            self._queue.put_nowait(message)
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(message)
            except queue.Full:
                pass

    def close(self):
        """Ask the voice worker to stop."""
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(None)
            except queue.Full:
                pass
        self._thread.join(timeout=2)
