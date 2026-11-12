"""Pathfinder camera/model diagnostic utility.

Use this separately from narration to inspect raw detector predictions.
Saved frames are for debugging and are not evidence of real-world safety.
"""

import argparse
from datetime import datetime
from pathlib import Path

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inspect YOLO predictions and save diagnostic camera frames."
    )
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--conf", type=float, default=0.10,
                        help="Low diagnostic threshold; not the narration threshold.")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--output", default="diagnostic_frames")
    return parser.parse_args()


def main():
    args = parse_args()
    if not 0 < args.conf < 1:
        raise SystemExit("--conf must be between 0 and 1.")
    if args.imgsz < 320:
        raise SystemExit("--imgsz must be at least 320.")

    print(f"Loading {args.model}...")
    model = YOLO(args.model)
    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        raise SystemExit(
            f"Could not open camera {args.camera}. Try --camera 1."
        )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print("Diagnostic mode. Press S to save a frame and Q to quit.")
    print(f"Prediction confidence: {args.conf:.2f} | image size: {args.imgsz}")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Camera frame could not be read.")
                break

            result = model.predict(
                frame, conf=args.conf, imgsz=args.imgsz, verbose=False
            )[0]
            annotated = result.plot(conf=True)
            cv2.imshow("Pathfinder | Detection Diagnostics", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                raw_path = output_dir / f"{stamp}_raw.jpg"
                annotated_path = output_dir / f"{stamp}_predictions.jpg"
                cv2.imwrite(str(raw_path), frame)
                cv2.imwrite(str(annotated_path), annotated)

                print(f"\nSaved: {raw_path} and {annotated_path}")
                if result.boxes is None or len(result.boxes) == 0:
                    print("No objects detected.")
                else:
                    for box in result.boxes:
                        class_id = int(box.cls.item())
                        confidence = float(box.conf.item())
                        name = result.names[class_id]
                        print(f"  {name}: {confidence:.3f}")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
