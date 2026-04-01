# ================================================================
#  phone_detection.py
#  JOB: Detect if a mobile phone is visible in the webcam frame.
#  USES: YOLOv8 — pretrained on COCO dataset (80 object classes)
#        "cell phone" is class index 67 in COCO.
#  CALLED BY: main.py
# ================================================================

from ultralytics import YOLO
import cv2

# ----------------------------------------------------------------
# Load YOLOv8 model — yolov8n = "nano" (smallest + fastest).
# First run: auto-downloads yolov8n.pt (~6MB) to your machine.
# Subsequent runs: loads from cache instantly.
# ----------------------------------------------------------------
from ultralytics import YOLO
import torch

# Allow YOLO model class (safe because it's official)
from ultralytics.nn.tasks import DetectionModel
torch.serialization.add_safe_globals([DetectionModel])

model = YOLO("yolov8n.pt")

# COCO dataset class index for "cell phone"
PHONE_CLASS_ID = 67

# Minimum confidence to count a detection (0.0 to 1.0)
CONFIDENCE_THRESHOLD = 0.5


def detect_phone(frame):
    """
    INPUT  : frame — one webcam image (numpy array, BGR)
    OUTPUT : phone_detected — True or False
             frame          — same image with box drawn if phone found
    """

    # Run YOLOv8 on the frame
    # verbose=False stops YOLO printing to terminal every frame
    results = model(frame, verbose=False)

    phone_detected = False

    for result in results:
        for box in result.boxes:

            class_id   = int(box.cls[0])        # what object is this?
            confidence = float(box.conf[0])     # how confident? (0 to 1)

            # Only care about phones with enough confidence
            if class_id == PHONE_CLASS_ID and confidence >= CONFIDENCE_THRESHOLD:
                phone_detected = True

                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw a red box around the phone
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                # Label above the box
                label = f"PHONE {confidence:.0%}"
                cv2.rectangle(frame, (x1, y1 - 22), (x1 + 130, y1), (0, 0, 255), -1)
                cv2.putText(frame, label,
                            (x1 + 4, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                            (255, 255, 255), 1)

    return phone_detected, frame