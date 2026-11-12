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

### Technical decisions
- Use Python, Ultralytics YOLO, and OpenCV for the computer-vision prototype.
- Use the lightweight `yolo26n.pt` model by default.
- Horizontal position is calculated from the centre of each detection's bounding box, divided into three equal regions.
- These labels describe image-space position only. They do not establish real-world direction, physical distance, collision risk, or a safe route.
- Keep object detection, spatial interpretation, OCR, speech input, and audio narration as separate milestones.

### Verification status
- **Milestone 1:** Verified locally by the developer. The webcam opened and live object detections rendered successfully.
- **Milestone 2:** Implemented in the repository, but still needs local testing.

### Next steps
1. Pull the latest changes and run `python main.py`.
2. Confirm that detected objects receive LEFT, CENTRE, or RIGHT labels.
3. Test objects placed in different parts of the camera frame.
4. After the labels are validated, design obstacle prioritisation and cautious proximity cues.
5. Add speech output after the visual spatial layer is stable.
