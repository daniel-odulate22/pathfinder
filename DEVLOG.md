# Development Log

This file records implemented work and verified results. Planned work is kept separate from completed work.

## 12 November 2026

### Milestone 1: Live object detection
- Added live webcam object detection using Ultralytics YOLO and OpenCV.
- Developer verified that YOLO26n loaded, webcam opened, and bounding boxes and confidence scores rendered.

### Milestone 2: Basic horizontal spatial awareness
- Added LEFT / CENTRE / RIGHT image-space classification based on bounding-box centres.
- Developer confirmed these labels worked locally.

### Milestone 3: Visual prominence and attention heuristic
- Added bounding-box area ratio and HIGH / MEDIUM / LOW visual-attention heuristic.
- Added standard-library unit tests. Local verification remains pending.

### Milestone 4: Initial voice narration
- Added concise scene-description generation and offline text-to-speech using `pyttsx3`.
- Speech runs on a background thread so it does not block camera capture.
- Added confidence filtering, deduplication, `--mute`, and `--announce-interval`.
- Developer confirmed audio narration works locally.

### Milestone 5: Controlled repeat narration
- Changed narration scheduling so a changed scene can be announced after the minimum changed-scene interval.
- An unchanged scene is repeated after a separate configurable interval, defaulting to 12 seconds.
- Empty scenes are not announced.
- Added unit tests for changed-scene announcements, repeat timing, and empty-scene suppression.

### Technical decisions and limitations
- Use Python, Ultralytics YOLO, OpenCV, and local/offline `pyttsx3`.
- Horizontal position describes image-space location only.
- Bounding-box area ratio describes visual prominence, not physical distance.
- HIGH / MEDIUM / LOW is an attention heuristic, not a danger rating or proof that an object is an obstacle.
- Narration is one-way scene description. Speech recognition and conversational voice commands are not implemented.
- Pathfinder does not provide safe navigation or collision avoidance.

### Verification status
- **Milestone 1:** Verified locally by the developer.
- **Milestone 2:** Verified locally by the developer.
- **Milestone 3:** Implemented; local tests remain pending.
- **Milestone 4:** Verified locally by the developer.
- **Milestone 5:** Implemented; repeat cadence requires local verification.

### Next steps
1. Pull changes, run `python -m unittest discover -s tests -v`, and test the repeat cadence.
2. Add user-triggered speech input and a small set of grounded camera-context questions.
3. Evaluate microphone support and speech-recognition reliability on the target Windows machine.
4. Consider OCR only after the voice interaction loop is stable.
