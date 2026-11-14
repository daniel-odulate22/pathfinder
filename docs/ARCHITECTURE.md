# Pathfinder Architecture

## Product principle

Pathfinder is one product with a shared intelligence layer and multiple possible device interfaces. The current browser application is the first interface. A future wearable, such as smart glasses, should be another interface to the same underlying capabilities rather than a separate product with duplicated scene-understanding logic.

This is an architectural direction, not a claim that wearable hardware is currently implemented.

## Current prototype

The integrated application has two main runtime parts:
- **Browser frontend** in frontend/: React + TypeScript. It provides the user interface and browser access to camera, microphone, speech input, and speech output.
- **Python backend** in server.py: FastAPI. It receives image frames and questions, runs the available vision and text-reading capabilities, and returns structured results.

The backend reuses Python modules for detection, spatial calculations, narration/scene logic, and OCR. SQLite is used for application history.

## Current data flow

1. The browser obtains camera frames and user input.
2. The React frontend sends image frames or questions to the FastAPI backend.
3. The backend runs object detection and image-space spatial calculations.
4. Scene and question logic produces a structured response grounded in current detections.
5. RapidOCR runs when the user explicitly requests text reading.
6. The frontend presents results and handles browser speech output.

## Intended separation of responsibilities

### 1. Device adapters

Device adapters translate hardware-specific inputs and outputs into stable application interfaces.

Potential inputs include camera frames and timestamps, microphone audio or recognised utterances, and optional IMU or orientation data. Potential outputs include spoken audio, haptic signals if justified by user research, and visual status or controls.

A browser, phone application, and future glasses should be able to implement different adapters without duplicating scene-understanding logic.

### 2. Pathfinder intelligence

The intelligence layer should provide object detection and tracking, image-space spatial context, scene summarisation and change detection, question answering grounded in recent observations, on-demand OCR, confidence and uncertainty handling, and narration prioritisation and timing.

The layer should not assume that a frame came from a phone or that speech must be played by a browser.

### 3. Interfaces and experiences

The current web interface presents camera video, detections, status, controls, and browser speech. A future wearable interface may prioritise concise audio descriptions, discreet controls, low latency, and low power use. A companion phone may eventually configure a wearable or provide additional compute.

## Future wearable considerations

Smart glasses are a possible future interface. They are not part of the current implementation.

Before choosing hardware, evaluate camera field of view, focus, exposure and low-light performance; processing location; latency and network availability; battery life, heat, weight and comfort; microphone quality and audio privacy; open-ear audio; privacy indicators; and accessibility for people with different levels of residual vision.

A wearable should not be assumed to run every model locally. The compute split must be decided from measured latency, power, thermal, privacy, and connectivity requirements.

## Safety and uncertainty

Pathfinder is an experimental environmental awareness assistant. It is not a navigation or collision-avoidance system and does not replace established mobility aids or training.

Object detections can be wrong or incomplete. Image-space position is not physical distance. Bounding-box size is not a reliable distance measurement. The system should communicate uncertainty and avoid presenting unsupported inferences as facts.

## Current limitations

- The backend currently maintains shared scene state and is intended for one active camera session at a time.
- The default YOLO model is limited to its supported classes.
- Browser speech recognition availability and processing behaviour depend on the browser.
- OCR is invoked on demand and can miss or misread text.
- Wearable hardware and device adapters have not been implemented.
- Multi-user session isolation, authentication, and production deployment hardening remain future work.
