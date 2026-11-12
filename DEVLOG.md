# Development Log

This file records implemented work and verified results. Planned work is kept separate from completed work.

## 12 November 2026

### Milestone 1: Live object detection
- Added the initial Python dependency list in `requirements.txt`.
- Added a Python entry point in `main.py` for live webcam object detection using Ultralytics YOLO and OpenCV.
- The developer ran the application locally. The webcam opened, YOLO26n loaded, and live detections with bounding boxes and confidence scores were visible.

### Milestone 2: Basic horizontal spatial awareness
- Added `spatial.py` with a helper that classifies an object's bounding-box centre as LEFT, CENTRE, or RIGHT relative to the camera frame.
- Updated `main.py` to overlay the spatial label and confidence alongside each detected class.
- Added vertical guide lines to show the three image-space regions.
- The developer confirmed that the left / centre / right labels work locally.

### Milestone 3: Visual prominence and attention heuristic
- Added bounding-box area ratio as a measure of how much of the image frame a detection occupies.
- Added a simple HIGH / MEDIUM / LOW visual-attention heuristic based on horizontal position and frame-area ratio.
- Updated the live overlay to display the attention label and percentage of frame occupied.
- Added standard-library unit tests in `tests/test_spatial.py`.

### Technical decisions and limitations
- Use Python, Ultralytics YOLO, and OpenCV for the computer-vision prototype.
- Use the lightweight `yolo26n.pt` model by default.
- Horizontal position describes image-space location only.
- Bounding-box area ratio describes visual prominence only. It is not a physical distance estimate because apparent size also depends on an object's real dimensions, camera geometry, and perspective.
- HIGH / MEDIUM / LOW is an attention heuristic, not a danger rating or proof that an object is an obstacle.
- The system does not provide safe navigation, collision probability, or collision-avoidance guidance.

### Verification status
- **Milestone 1:** Verified locally by the developer. The webcam opened and live object detections rendered successfully.
- **Milestone 2:** Verified locally by the developer. Horizontal labels worked as expected.
- **Milestone 3:** Implemented in the repository. Unit tests and live overlay still need to be run locally.

### Next steps
1. Pull the latest changes and run `python -m unittest discover -s tests`.
2. Run `python main.py` and inspect the visual-attention labels.
3. Tune thresholds only after observing representative test scenes.
4. Design cautious proximity cues using additional evidence, rather than treating bounding-box size as physical distance.
5. Add speech output after the visual context layer is stable.
