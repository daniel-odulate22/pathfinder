"""Voice narration helpers for Pathfinder."""

import queue
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
