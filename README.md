# Pathfinder

A camera-powered, voice-interactive environmental awareness assistant designed to help people with visual impairments better understand their immediate surroundings.

The current prototype detects common objects, estimates their position within the camera frame, and can speak concise scene descriptions.

**Focus: find it and read it, indoors.** A user in an unfamiliar room asks "Where is the chair?" or "Is anyone here?", then points the camera at a sign or label and asks what it says.

> **Safety note:** Pathfinder is an experimental awareness aid, not a navigation or collision-avoidance system. It does not replace a white cane, guide dog, orientation and mobility training, or other established mobility tools. Detection can be incomplete or incorrect.

## Current capabilities

- [x] Live webcam object detection with YOLO
- [x] LEFT / CENTRE / RIGHT image-space labels
- [x] Visual prominence and attention heuristics
- [x] Initial offline text-to-speech narration
- [x] Narration scheduling verified: an unchanged scene repeats every 12–13 seconds through the web API
- [ ] Listen to the desktop `pyttsx3` narration on the target machine
- [x] Web app: React + TypeScript frontend, FastAPI backend, SQLite announcement history, Docker Compose
- [x] Typed and spoken position questions in the web app ("What is on my left?")
- [x] Object search by name ("Where is the chair?", "Is there a bottle on my right?")
- [x] Large **Ask by voice** button with a start tone, and an opt-in HTTPS tunnel for phone cameras
- [x] Web app verified in headless Chrome with a simulated camera: detection, overlay, announcements, questions, text reading, mute, stop
- [ ] Check audible speech, spoken questions, and a phone camera by hand
- [x] On-demand text reading in the web app: **Read text** button or "What does the sign say?"
- [x] OCR evaluated on real sign photos; Tesseract replaced with RapidOCR as a result

## Tech stack

- **Python** for the prototype
- **Ultralytics YOLO** for object detection
- **OpenCV** for webcam capture and display
- **pyttsx3** for offline text-to-speech (desktop prototype)
- **React + TypeScript (Vite)** for the web frontend; the browser provides camera, speech output, and speech input
- **FastAPI** for the detection API and **SQLite** for announcement history
- **Docker Compose** to run the web app

## Getting started

### 1. Requirements

- Python 3.10 or newer
- A working webcam
- Windows, macOS, or Linux

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

If Python 3.11 is not installed, use an available supported Python version.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Pathfinder

```bash
python main.py
```

Pathfinder opens the webcam and speaks concise descriptions when the detected scene changes. The first run downloads the default `yolo26n.pt` model weights.

Press `q` in the video window to stop.

To run without audio:

```bash
python main.py --mute
```

To select another camera or adjust the minimum interval between spoken updates:

```bash
python main.py --camera 1
python main.py --announce-interval 8
```

## Run the web app with Docker Compose

```bash
docker compose up --build
```

Open <http://localhost:8080>, press **Start camera**, and allow camera access. The browser sends frames to the backend, which runs YOLO and decides when a scene should be announced; the browser speaks it. Announcements and answered questions are stored in SQLite in the `pathfinder-data` volume, alongside the downloaded model weights.

Ask a question by typing it, or with **Ask by voice** in Chrome or Safari. Questions are answered only from the current detections. You can filter by "left", "right", or "front", and search for an object by name: "Where is the chair?" answers with its position or "I cannot see a chair right now."

Only the 80 everyday object types the default YOLO model knows can be found, such as people, chairs, tables, couches, bottles, cups, laptops, phones, backpacks, and TVs. Doors, stairs, and exits are **not** among them; asking for one gets "I cannot look for that."

Press **Read text**, or ask something like "What does the sign say?", to read text in the latest camera frame with RapidOCR, a scene-text model that runs offline. It can still miss or misread text, and it only speaks lines containing Latin letters or digits.

The first build downloads PyTorch and is slow. The app is published on `localhost` only because the API has no authentication. Browsers only allow camera access on `localhost` or HTTPS.

### Use a phone camera

Browsers only allow camera access over HTTPS, so a phone cannot use the laptop's `localhost` address. To get a temporary public HTTPS address:

```bash
docker compose --profile phone up --build
docker compose logs tunnel   # shows the https://….trycloudflare.com URL
```

Open that URL on the phone. Anyone who has the URL can use the app while it runs, and camera frames pass through Cloudflare, so stop it after the demo.

### Demo script

1. Start the camera and wait for the first spoken scene description.
2. Press **Ask by voice**, wait for the tone, and ask "Where is the chair?"
3. Ask "Is there a bottle on my left?" with none there, to show it does not guess.
4. Point the camera at a printed sign and press **Read text**.

For frontend development, run the API with `uvicorn server:app` and the UI with `npm run dev` inside `frontend/`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
pathfinder/
├── main.py
├── spatial.py
├── speech.py
├── ocr.py
├── server.py
├── Dockerfile
├── docker-compose.yml
├── frontend/
├── requirements.txt
├── DEVLOG.md
└── tests/
    ├── test_ocr.py
    ├── test_spatial.py
    └── test_speech.py
```

## Development log

See [DEVLOG.md](DEVLOG.md) for implementation notes, technical decisions, verification status, and next steps.

## License

No project license has been selected yet. Check the licensing terms of all dependencies and model weights before redistribution or commercial use.
