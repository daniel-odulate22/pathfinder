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

### Milestone 6: Web app, SQLite history, and position questions
- Added `server.py`, a FastAPI API that reuses the existing detection, description, and announcement-scheduling code.
- Added a React + TypeScript frontend in `frontend/`. The browser captures the camera, draws detections, and speaks announcements with the Web Speech API.
- Announcements and answered questions are stored in a SQLite database in a Docker volume.
- Added `answer_question`, which answers typed or spoken questions from the current detections, filtered by left / right / front. Added a unit test.
- Added Docker Compose with a backend container and an nginx frontend container, published on localhost only.

### Milestone 7: On-demand text reading
- Added `ocr.py`, which runs the Tesseract command-line tool on the latest camera frame and keeps only confident words.
- The web app reads text when the user presses **Read text** or asks a question containing words such as "read", "text", or "sign". It never reads text unprompted.
- Added unit tests for the OCR output parsing.

### Milestone 8: Indoor "find it and read it" focus
- Narrowed the project to one scenario: finding everyday objects and reading text in an unfamiliar room.
- `answer_question` now searches for an object named in the question and says plainly when it is absent or not detectable.
- Made **Ask by voice** a large primary button that plays a start tone and stops narration before listening.
- Added an opt-in Cloudflare quick tunnel (`--profile phone`) so a phone camera can reach the app over HTTPS.

## 13 November 2026

### Milestone 9: OCR evaluation and switch to RapidOCR
- Evaluated text reading on 16 photos from Wikimedia Commons searches for exit, push, stop, no smoking, fire exit, toilet, wet floor, and no entry signs.
- Tesseract missed almost all of them: it read nothing for a red EXIT sign, a TOILET sign, and a STOP sign, and only "NO SMOKING" from a three-line sign. Grayscale, inversion, thresholding, and 2x upscaling did not fix this.
- RapidOCR read EXIT, TOILET, STOP, PUSH, "FIRE EXIT / PLEASE KEEP CLEAR", and "DILARANG MEROKOK / NO SMOKING" correctly, in 1 to 2.5 seconds per image on CPU. It produced no usable text for distant or non-Latin signs.
- Replaced Tesseract with RapidOCR in `ocr.py`. Lines below 0.6 confidence or without Latin letters or digits are not spoken.

### Milestone 10: Browser verification and answer hold
- Drove the web app in headless Chrome with a simulated camera playing a still photo. Camera start, the detection overlay, spoken-announcement calls, typed questions, **Read text**, mute, and stop all worked with no page errors.
- Found and fixed a bug: a scene announcement could cut off an answer a second after it started. Answering a question now restarts the announcement timer.
- Sent one unchanged image for 40 requests; announcements repeated 12 to 13 seconds apart, matching the repeat interval.
- Ran the same browser check against the laptop's real webcam: frames streamed at 640x480 with no errors, but nothing was detected in view, so detection on a live scene is still unconfirmed.

### Technical decisions and limitations
- Use Python, Ultralytics YOLO, OpenCV, and local/offline `pyttsx3`.
- Horizontal position describes image-space location only.
- Bounding-box area ratio describes visual prominence, not physical distance.
- HIGH / MEDIUM / LOW is an attention heuristic, not a danger rating or proof that an object is an obstacle.
- The desktop prototype narration is one-way. The web app answers position questions only; it is not conversational.
- Spoken questions use the browser's speech recognition, which is Chrome/Safari only and may send audio to the browser vendor.
- Object search is limited to the 80 COCO classes of the default model. Doors, stairs, and exits cannot be found.
- The phone tunnel is public and unauthenticated while it runs.
- OCR uses RapidOCR (ONNX Runtime, offline). The evaluation used a small set of web photos, not a live camera feed.
- The web backend keeps one global scene state, so it supports one camera at a time.
- Pathfinder does not provide safe navigation or collision avoidance.

### Verification status
- **Milestone 1:** Verified locally by the developer.
- **Milestone 2:** Verified locally by the developer.
- **Milestone 3:** Implemented; local tests remain pending.
- **Milestone 4:** Verified locally by the developer.
- **Milestone 5:** Repeat cadence verified through the web API (see Milestone 10). Desktop audio cadence not listened to.
- **Milestone 6:** Unit tests pass in the backend container, and the API was checked through nginx with a still test image (detection, announcement, question, SQLite history). Browser camera, speech output, and spoken questions require local verification.
- **Milestone 7:** Superseded by Milestone 9.
- **Milestone 9:** Unit tests pass, including a light-on-dark sign read by the real model. Verified on still photos only.
- **Milestone 10:** Verified in headless Chrome with a simulated camera. Audible speech, spoken questions, phone cameras, and the tunnel are not verified.

### Next steps
1. Pull changes, run `python -m unittest discover -s tests -v`, and test the repeat cadence.
2. Run `docker compose up --build` and test the web app with a real camera, speakers, and microphone.
3. Evaluate browser speech-recognition reliability on the target Windows machine.
4. Try **Read text** on real signs through the camera, including at an angle and from a distance.

## 14 November 2026

### Milestone 11: Integrated local development workflow verified
- The merged React + TypeScript frontend and FastAPI backend were pulled into the developer's local repository.
- The developer started the backend and frontend in separate terminals and confirmed that both ran successfully.
- The developer reported that the frontend loaded, the backend operated, and the automated test suite passed.
- The two-terminal local workflow is the recommended development path for now. Docker remains optional.
- The visual design has not yet been redesigned. A full interface redesign is planned; the current design is functional but does not yet meet the intended product art direction.

### Milestone 12: Product architecture direction
- Agreed to treat Pathfinder as one product with a device-independent intelligence layer and multiple possible interfaces.
- The current browser application is the first interface, using a computer or phone camera, microphone, display, and audio output.
- Smart glasses or another wearable are a future interface direction, not an implemented capability.
- Future architecture should keep scene understanding and interaction logic separate from device-specific camera, microphone, and audio adapters.
- No wearable hardware, embedded deployment, or wearable-specific model optimisation has been implemented yet.

### Evaluation and privacy notes
- Local diagnostic captures are useful for investigating false detections and missed detections.
- Raw camera captures should remain local by default. They may contain identifiable people or private surroundings and must not be uploaded to the public repository without consent and privacy review.
- A curated evaluation dataset is planned. It should include ground-truth object labels, model predictions, capture conditions, and outcomes so model changes can be compared objectively.
- The existing diagnostic captures have not yet been converted into a reviewed or annotated evaluation dataset.

### Next steps
1. Keep local diagnostic captures excluded from Git and define a privacy-reviewed evaluation dataset workflow.
2. Redesign the browser interface around a persistent camera workspace, accessible controls, clear live status, and compact scene information.
3. Review the frontend/backend boundary so device-specific input and output can evolve independently from scene understanding.
4. Continue vision evaluation, including missed detections, false classifications, duplicate boxes, blur, and performance on the target machine.
5. Revisit wearable hardware only after the shared software interfaces and interaction requirements are clearer.
