"""Pathfinder: live object detection, spatial context, and voice narration.

This prototype describes detections in the camera image. It does not provide
safe navigation, physical distance measurement, or collision avoidance.
"""

import argparse
import sys
import time

import cv2
from ultralytics import YOLO

from spatial import get_detection_context
from speech import VoiceNarrator, build_scene_description


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
    parser.add_argument(
        "--mute",
        action="store_true",
        help="Disable voice narration while keeping visual detections.",
    )
    parser.add_argument(
        "--announce-interval",
        type=float,
        default=5.0,
        help="Minimum seconds between spoken scene updates (default: 5).",
    )
    return parser.parse_args()


def annotate_spatial_context(frame, result):
    """Overlay image-space position and visual-attention labels."""
    frame_height, frame_width = frame.shape[:2]

    if result.boxes is None:
        return frame

    coordinates = result.boxes.xyxy.cpu().tolist()
    class_ids = result.boxes.cls.cpu().tolist()
    confidences = result.boxes.conf.cpu().tolist()

    for box, class_id, confidence in zip(
        coordinates, class_ids, confidences
    ):
        context = get_detection_context(box, frame_width, frame_height)
        class_name = result.names[int(class_id)]
        area_percent = context["area_ratio"] * 100

        label = (
            f"{class_name} | {context['position']} | "
            f"{context['attention']} ATTENTION | {area_percent:.0f}% frame"
        )

        x1, y1, _, _ = box
        text_y = max(25, int(y1) - 10)

        cv2.putText(
            frame,
            label,
            (int(x1), text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

    third = frame_width // 3
    two_thirds = (frame_width * 2) // 3
    guide_color = (180, 180, 180)

    cv2.line(frame, (third, 0), (third, frame_height), guide_color, 1)
    cv2.line(frame, (two_thirds, 0), (two_thirds, frame_height), guide_color, 1)

    return frame


def collect_detections(result, frame_width, frame_height):
    """Convert YOLO output into plain data for the narration layer."""
    detections = []

    if result.boxes is None:
        return detections

    coordinates = result.boxes.xyxy.cpu().tolist()
    class_ids = result.boxes.cls.cpu().tolist()
    confidences = result.boxes.conf.cpu().tolist()

    for box, class_id, confidence in zip(
        coordinates, class_ids, confidences
    ):
        context = get_detection_context(box, frame_width, frame_height)
        detections.append({
            "class_name": result.names[int(class_id)],
            "position": context["position"],
            "attention": context["attention"],
            "confidence": float(confidence),
        })

    return detections


def main():
    args = parse_args()

    if args.announce_interval < 0:
        print("--announce-interval must not be negative.", file=sys.stderr)
        return 1

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

    narrator = None
    if not args.mute:
        try:
            narrator = VoiceNarrator()
            print("Voice narration enabled. Use --mute to disable it.")
        except Exception as exc:
            print(f"Could not start voice narration: {exc}", file=sys.stderr)

    last_announcement = ""
    last_announcement_time = 0.0

    print("Pathfinder is running. Press 'q' in the video window to quit.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Could not read a frame from the camera.", file=sys.stderr)
                break

            results = model.predict(frame, verbose=False)
            result = results[0]
            frame_height, frame_width = frame.shape[:2]

            detections = collect_detections(
                result, frame_width, frame_height
            )
            description = build_scene_description(detections)

            now = time.monotonic()
            if (
                narrator
                and description
                and description != last_announcement
                and now - last_announcement_time >= args.announce_interval
            ):
                narrator.speak(description)
                last_announcement = description
                last_announcement_time = now

            annotated_frame = result.plot()
            annotated_frame = annotate_spatial_context(
                annotated_frame, result
            )

            cv2.imshow("Pathfinder | Voice Awareness", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        print("\nStopping Pathfinder...")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        if narrator:
            narrator.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
