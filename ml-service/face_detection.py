# ================================================================
#  face_detection.py
#  JOB: Count how many faces are visible in one webcam frame.
#  CALLED BY: main.py
# ================================================================

import mediapipe as mp
import cv2

# --- Create the face detector ONCE (reusing it is faster) -------
mp_face_detection = mp.solutions.face_detection
mp_drawing        = mp.solutions.drawing_utils

face_detector = mp_face_detection.FaceDetection(
    model_selection=1,            # 1 = detects faces up to ~5 metres away
    min_detection_confidence=0.5  # needs 50% confidence to count a face
)


def count_faces(frame):
    """
    INPUT  : frame  — one image from the webcam (numpy array, BGR format)
    OUTPUT : face_count  — integer: 0, 1, 2, 3 ...
             frame       — same image with coloured boxes drawn on each face
    """

    # MediaPipe needs RGB, but OpenCV gives BGR — convert colour order
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run the AI detector
    results = face_detector.process(rgb_frame)

    face_count = 0  # default: no face found

    if results.detections:                      # at least one face found
        face_count = len(results.detections)    # count all faces

        # Draw a box around each face (just so you can see it on screen)
        for detection in results.detections:
            mp_drawing.draw_detection(frame, detection)

    return face_count, frame