"""Pathfinder web API: the browser sends camera frames, YOLO runs here.

Like the desktop prototype, this describes detections in the camera image. It
does not provide safe navigation, distance measurement, or collision avoidance.
"""

import os
import re
import sqlite3
import threading
import time

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from ultralytics import YOLO

from main import collect_detections
from ocr import read_text
from speech import answer_question, build_scene_description, should_announce

DATA_DIR = os.environ.get("PATHFINDER_DATA", ".")
MAX_FRAME_BYTES = 2 * 1024 * 1024
READ_WORDS = {"read", "text", "sign", "signs", "say", "says", "written"}

app = FastAPI()
model = YOLO(os.path.join(DATA_DIR, "yolo26n.pt"))
db = sqlite3.connect(os.path.join(DATA_DIR, "pathfinder.db"), check_same_thread=False)
db.execute(
    "CREATE TABLE IF NOT EXISTS announcements ("
    "id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, text TEXT NOT NULL)"
)
db.commit()

# shortcut: one global scene state and lock, so one camera at a time; key by session if multi-user.
lock = threading.Lock()
state = {"detections": [], "frame": None, "last": "", "time": time.monotonic()}


def log(text):
    db.execute("INSERT INTO announcements (text) VALUES (?)", (text,))
    db.commit()


def process_frame(data):
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "Body must be a JPEG or PNG image.")
    height, width = frame.shape[:2]
    with lock:
        result = model.predict(frame, verbose=False)[0]
        detections = collect_detections(result, width, height)
        description = build_scene_description(detections)
        now = time.monotonic()
        announce = should_announce(description, state["last"], now, state["time"])
        if announce:
            state.update(last=description, time=now)
            log(description)
        state["detections"] = detections
        state["frame"] = frame
    return {"detections": detections, "description": description, "announce": announce}


@app.post("/api/detect")
async def detect(request: Request):
    data = await request.body()
    if len(data) > MAX_FRAME_BYTES:
        raise HTTPException(413, "Frame too large.")
    return await run_in_threadpool(process_frame, data)


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=200)


@app.post("/api/ask")
def ask(body: Question):
    with lock:
        detections, frame = state["detections"], state["frame"]
    if READ_WORDS & set(re.findall(r"[a-z]+", body.question.lower())):
        if frame is None:
            answer = "Start the camera first so I have something to read."
        else:
            # OCR runs outside the lock so detection keeps going meanwhile.
            answer = read_text(frame)
    else:
        answer = answer_question(body.question, detections, model.names.values())
    with lock:
        # Restart the announcement timer so narration does not cut the answer off.
        state["time"] = time.monotonic()
        log(f"Q: {body.question} A: {answer}")
    return {"answer": answer}


@app.get("/api/history")
def history():
    with lock:
        rows = db.execute(
            "SELECT id, created_at, text FROM announcements ORDER BY id DESC LIMIT 20"
        ).fetchall()
    return [{"id": r[0], "created_at": r[1], "text": r[2]} for r in rows]
