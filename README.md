# Pathfinder

Pathfinder is a camera-powered accessibility assistant that uses computer vision and voice interaction to help people with visual impairments better understand their immediate surroundings.

It analyses a live camera feed, identifies supported everyday objects, describes their position within the image, and lets users ask questions about what is currently visible. Users can also request text reading from signs and labels.

> **Safety and scope:** Pathfinder is an experimental environmental-awareness aid. It is not a navigation, obstacle-detection, or collision-avoidance system. It does not measure reliable physical distance and does not replace a white cane, guide dog, orientation and mobility training, or other established mobility tools. Its detections and OCR results can be incomplete or incorrect.

## What it can do

- **Live object detection:** Detects objects supported by the default YOLO model from a webcam feed.
- **Image-space position:** Groups detections as LEFT, CENTRE, or RIGHT based on their position in the camera frame.
- **Scene descriptions:** Produces concise spoken descriptions of detected objects, with repeat and change-aware announcement logic.
- **Ask about the current view:** Accepts typed questions and browser speech input, including questions about an object's name or its left/right position.
- **Read text on request:** Uses RapidOCR to read text from the latest camera frame when the user requests it.
- **Recent activity:** Stores announcement and question history in SQLite.
- **Camera-first web interface:** Provides a live camera workspace, detection overlay, scene notes, question controls, and responsive layout.

The object detector can only identify classes included in its model. It cannot reliably find arbitrary objects, doors, stairs, exits, or hazards unless those are supported by the model and correctly detected.

## Technology

| Area | Technology |
|---|---|
| Object detection | Ultralytics YOLO (default model: YOLO26n) |
| Image processing | OpenCV |
| OCR | RapidOCR with ONNX Runtime |
| Backend API | Python, FastAPI, Uvicorn |
| Frontend | React, TypeScript, Vite |
| Camera and speech in web app | Browser MediaDevices and Web Speech APIs |
| Desktop prototype speech | pyttsx3 |
| History | SQLite |
| Container workflow | Docker Compose |

## How it works

1. The browser requests camera permission and captures frames.
2. Frames are sent to the FastAPI backend for object detection.
3. The backend calculates image-space positions and prepares scene descriptions.
4. The frontend draws detection overlays and uses browser speech synthesis for spoken output.
5. Typed or recognised spoken questions are sent to the backend and answered from the current detection context.
6. When text reading is requested, RapidOCR processes the latest frame and returns readable text.

The current backend keeps shared scene state and is intended for one active camera session at a time. It is a local prototype, not a multi-user production service.

## Run locally

### Requirements

- Python 3.10 or newer
- Node.js and npm
- A webcam
- Windows, macOS, or Linux

### 1. Clone the repository

```bash
git clone https://github.com/daniel-odulate22/pathfinder.git
cd pathfinder
```

### 2. Set up Python

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If Python 3.11 is unavailable, use a supported Python version installed on your machine.

### 3. Start the backend

From the repository root:

```powershell
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 4. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local Vite URL printed in the terminal, usually `http://localhost:5173`.

Keep both terminals running while using the web app. Camera access is generally permitted on localhost. Allow camera and microphone permissions when prompted.

### 5. Run the Python prototype (optional)

The standalone desktop prototype can be started from the repository root:

```bash
python main.py
```

Mute desktop speech:

```bash
python main.py --mute
```

Choose a camera or adjust the announcement interval:

```bash
python main.py --camera 1
python main.py --announce-interval 8
```

Press `q` in the video window to stop the desktop prototype.

## Run with Docker Compose (optional)

```bash
docker compose up --build
```

Open `http://localhost:8080`. The Compose setup runs the backend and frontend and stores SQLite data and downloaded model weights in a Docker volume.

The optional phone-camera tunnel is public and unauthenticated while active. Only use it for a controlled demonstration, do not expose sensitive camera feeds, and stop it when finished:

```bash
docker compose --profile phone up --build
docker compose logs tunnel
```

Open the generated HTTPS address on the phone. Anyone with the address may be able to access the running app, and camera frames pass through the tunnel provider.

## Tests and build

Run the Python test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

Build the frontend from the `frontend/` directory:

```bash
npm ci
npm run build
```

## Repository layout

```text
pathfinder/
├── main.py                    # Standalone webcam prototype
├── server.py                  # FastAPI application and API routes
├── spatial.py                 # Image-space position and prominence logic
├── speech.py                  # Scene descriptions and announcement scheduling
├── ocr.py                     # On-demand text recognition
├── frontend/
│   └── src/
│       ├── App.tsx             # Camera-first React interface
│       ├── hooks/useSpeech.ts  # Browser speech controls
│       ├── services/           # Backend API client
│       └── types.ts            # Shared frontend types
├── tests/                     # Python unit tests
├── docs/
│   └── ARCHITECTURE.md         # Current architecture and future device direction
├── DEVLOG.md                   # Development history and verification notes
├── requirements.txt
└── docker-compose.yml
```

## Limitations and responsible use

- LEFT / CENTRE / RIGHT describe where an object appears in the image, not its physical location in the room.
- Bounding-box size is not a reliable distance measurement.
- The HIGH / MEDIUM / LOW attention heuristic is not a danger score.
- Object detection is limited to the model's supported classes and can miss or misclassify objects.
- OCR can omit, distort, or misread text, especially at a distance, at an angle, or in poor lighting.
- Browser speech recognition support varies by browser and may rely on browser-vendor services.
- The current API uses shared scene state and is designed for a single active camera session.
- Authentication, multi-user isolation, production deployment hardening, and wearable hardware are not implemented.

**Privacy:** Camera frames are processed by the local backend during local development. Avoid publishing raw camera captures or evaluation images that may contain identifiable people or private surroundings. The repository ignores local diagnostic and private evaluation folders.

## Architecture and development notes

- [Architecture](docs/ARCHITECTURE.md)
- [Development log](DEVLOG.md)

## Project status

Pathfinder is an experimental prototype. The core detection, question-answering, OCR, and camera-first web interface are implemented. The frontend production build and Python unit tests have been run locally. A full manual verification of camera, audible speech, spoken questions, and OCR on the target device should be completed before relying on a particular setup.

## License

No project license has been selected yet. Check the licensing terms of all dependencies and model weights before redistribution or commercial use.
