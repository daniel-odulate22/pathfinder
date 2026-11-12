"""Pathfinder: live camera object detection prototype.

This first milestone detects common objects in a webcam feed.
It does not provide safe navigation or collision-avoidance guidance.
"""

import argparse
import sys

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run live object detection using a webcam and YOLO."
    )
    parser.add_argument(
        "--model",
        default="yolo26n.pt",
        help="Ultralytics model weights (default: yolo26n.pt)",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Webcam device index (default: 0)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Loading model: {args.model}")
    try:
        model = YOLO(args.model)
    except Exception as exc:
        print(f"Could not load the YOLO model: {exc}", file=sys.stderr)
        return 1

    print(f"Opening camera {args.camera}...")
    camera = cv2.VideoCapture(args.camera)

    if not camera.isOpened():
        print(
            "Could not open the camera. Check camera permissions and the device index.",
            file=sys.stderr,
        )
        return 1

    print("Pathfinder is running. Press 'q' in the video window to quit.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Could not read a frame from the camera.", file=sys.stderr)
                break

            results = model.predict(frame, verbose=False)
            annotated_frame = results[0].plot()

            cv2.imshow("Pathfinder | Live Object Detection", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        print("\nStopping Pathfinder...")
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
