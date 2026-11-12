"""Pathfinder: live camera object detection with basic spatial labels.

This prototype detects common objects and estimates their horizontal
position within the camera frame. It does not provide safe navigation,
real-world distance measurement, or collision-avoidance guidance.
"""

import argparse
import sys

import cv2
from ultralytics import YOLO

from spatial import get_horizontal_position


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


def annotate_spatial_positions(frame, result):
    """Overlay LEFT / CENTRE / RIGHT labels for detected objects."""
    frame_height, frame_width = frame.shape[:2]

    if result.boxes is None:
        return frame

    boxes = result.boxes
    coordinates = boxes.xyxy.cpu().tolist()
    class_ids = boxes.cls.cpu().tolist()
    confidences = boxes.conf.cpu().tolist()

    for (x1, y1, x2, y2), class_id, confidence in zip(
        coordinates, class_ids, confidences
    ):
        position = get_horizontal_position(x1, x2, frame_width)
        class_name = result.names[int(class_id)]
        label = f"{class_name} | {position} | {confidence:.2f}"

        text_y = max(25, int(y1) - 10)
        cv2.putText(
            frame,
            label,
            (int(x1), text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

    # Visual guides show the three image-space regions.
    third = frame_width // 3
    two_thirds = (frame_width * 2) // 3
    guide_color = (180, 180, 180)

    cv2.line(frame, (third, 0), (third, frame_height), guide_color, 1)
    cv2.line(frame, (two_thirds, 0), (two_thirds, frame_height), guide_color, 1)

    return frame


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
            annotated_frame = annotate_spatial_positions(
                annotated_frame, results[0]
            )

            cv2.imshow("Pathfinder | Spatial Awareness", annotated_frame)

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
