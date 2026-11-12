# Pathfinder

A camera-powered, voice-interactive environmental awareness assistant designed to help people with visual impairments better understand their immediate surroundings.

The current prototype detects common objects, estimates their position within the camera frame, and can speak concise scene descriptions.

> **Safety note:** Pathfinder is an experimental awareness aid, not a navigation or collision-avoidance system. It does not replace a white cane, guide dog, orientation and mobility training, or other established mobility tools. Detection can be incomplete or incorrect.

## Current capabilities

- [x] Live webcam object detection with YOLO
- [x] LEFT / CENTRE / RIGHT image-space labels
- [x] Visual prominence and attention heuristics
- [x] Initial offline text-to-speech narration
- [ ] Local verification of the new narration layer
- [ ] Speech recognition and voice questions
- [ ] Evaluate OCR for signs and nearby text

## Tech stack

- **Python** for the prototype
- **Ultralytics YOLO** for object detection
- **OpenCV** for webcam capture and display
- **pyttsx3** for offline text-to-speech

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
├── requirements.txt
├── DEVLOG.md
└── tests/
    ├── test_spatial.py
    └── test_speech.py
```

## Development log

See [DEVLOG.md](DEVLOG.md) for implementation notes, technical decisions, verification status, and next steps.

## License

No project license has been selected yet. Check the licensing terms of all dependencies and model weights before redistribution or commercial use.
