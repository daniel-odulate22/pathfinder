# Pathfinder

A camera-powered, voice-interactive environmental awareness assistant designed to help people with visual impairments better understand their immediate surroundings.

Pathfinder's first prototype focuses on live object detection. Later milestones will explore spatial context, obstacle prioritisation, text recognition, and concise voice output.

> **Safety note:** Pathfinder is an experimental awareness aid, not a navigation or collision-avoidance system. It does not replace a white cane, guide dog, orientation and mobility training, or other established mobility tools. Detection can be incomplete or incorrect.

## Current milestone

- [x] Initial Python project setup
- [x] Live webcam object-detection entry point
- [ ] Verify local installation and webcam inference
- [ ] Add left / centre / right spatial descriptions
- [ ] Prioritise potentially relevant obstacles
- [ ] Add speech output and basic voice commands
- [ ] Evaluate OCR for signs and nearby text

## Tech stack

- **Python** for the computer-vision prototype
- **Ultralytics YOLO** for object detection
- **OpenCV** for webcam capture and display

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

The first run downloads the default `yolo26n.pt` model weights. Press `q` while the video window is focused to stop the program.

To select another camera or model:

```bash
python main.py --camera 1
python main.py --model yolo26n.pt
```

## Project structure

```text
pathfinder/
├── main.py
├── requirements.txt
├── DEVLOG.md
└── README.md
```

## Development log

See [DEVLOG.md](DEVLOG.md) for implementation notes, technical decisions, verification status, and next steps.

## License

No project license has been selected yet. Check the licensing terms of all dependencies and model weights before redistribution or commercial use.
