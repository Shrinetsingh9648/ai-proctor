# # ================================================================
# #  main.py
# #  JOB: Ties everything together.
# #       Opens webcam → runs detection → prints JSON → draws HUD.
# #
# #  HOW TO RUN:  python main.py
# #  QUIT:        Press Q inside the webcam window
# # ================================================================
#
# import cv2
# import json
# import time
#
# from face_detection import count_faces    # our file
# from head_pose      import get_head_pose  # our file
# from scorer         import SuspicionScorer  # our file
#
# # ── Settings (change these if needed) ────────────────────────────
# CAMERA_INDEX     = 0      # 0 = built-in webcam, 1 = external webcam
# JSON_PRINT_EVERY = 0.5    # print JSON every 0.5 seconds
# SHOW_WINDOW      = True   # False = headless mode (no window, JSON only)
# # ─────────────────────────────────────────────────────────────────
#
#
# def draw_hud(frame, face_count, direction, yaw, pitch, score_data):
#     """
#     Draw a dark info panel in the top-left corner of the webcam window.
#     HUD = Heads-Up Display (the overlay you see on screen).
#     """
#     score = score_data["suspicion_score"]
#
#     # Dark background rectangle
#     cv2.rectangle(frame, (0, 0), (370, 135), (15, 15, 15), -1)
#
#     # Bar colour: green → orange → red
#     if score == 0:
#         bar_color = (80, 200, 80)
#     elif score < 50:
#         bar_color = (0, 165, 255)
#     else:
#         bar_color = (60, 60, 220)
#
#     # Text lines
#     cv2.putText(frame, f"Faces  : {face_count}",
#                 (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (220,220,220), 1)
#     cv2.putText(frame, f"Gaze   : {direction}",
#                 (10, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (220,220,220), 1)
#
#     if yaw is not None:
#         cv2.putText(frame, f"Yaw: {yaw:+.1f}   Pitch: {pitch:+.1f}",
#                     (10, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (150,150,150), 1)
#
#     secs = score_data["look_away_secs"]
#     if secs > 0:
#         cv2.putText(frame, f"Looking away: {secs:.1f}s",
#                     (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (100,180,255), 1)
#
#     # Suspicion bar
#     cv2.rectangle(frame, (10, 110), (350, 126), (50,50,50), -1)
#     bw = int(340 * score / 100)
#     if bw > 0:
#         cv2.rectangle(frame, (10, 110), (10 + bw, 126), bar_color, -1)
#     cv2.putText(frame, f"Score:{score}",
#                 (355, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200,200,200), 1)
#
#     # Red border flash when suspicious
#     if score_data["is_suspicious"]:
#         h, w = frame.shape[:2]
#         cv2.rectangle(frame, (0,0), (w-1, h-1), (0, 0, 200), 3)
#
#     return frame
#
#
# def main():
#     print("=" * 50)
#     print("  AI Proctoring System — Phase 1")
#     print("  Press Q in the video window to quit")
#     print("=" * 50)
#     print()
#
#     # Open the webcam
#     cap = cv2.VideoCapture(CAMERA_INDEX)
#
#     if not cap.isOpened():
#         print(json.dumps({
#             "error": f"Cannot open camera {CAMERA_INDEX}",
#             "fix":   "Check camera permissions, or set CAMERA_INDEX = 1"
#         }, indent=2))
#         return
#
#     print(f"Camera {CAMERA_INDEX} opened.")
#     print(f"Printing JSON every {JSON_PRINT_EVERY}s ...\n")
#
#     scorer         = SuspicionScorer()
#     last_print     = 0.0
#
#     while True:
#         ret, frame = cap.read()   # grab one frame
#
#         if not ret:
#             print(json.dumps({"error": "Lost camera connection"}))
#             break
#
#         # Step 1 — count faces
#         face_count, frame = count_faces(frame)
#
#         # Step 2 — get gaze direction
#         direction, yaw, pitch, frame = get_head_pose(frame)
#
#         # Step 3 — calculate suspicion score
#         score_data = scorer.update(face_count, direction)
#
#         now = time.time()
#
#         # Step 4 — print JSON every N seconds
#         if now - last_print >= JSON_PRINT_EVERY:
#             last_print = now
#             print(json.dumps({
#                 "timestamp":         round(now, 3),
#                 "face_count":        face_count,
#                 "looking_direction": direction,
#                 "yaw_deg":           yaw,
#                 "pitch_deg":         pitch,
#                 "look_away_secs":    score_data["look_away_secs"],
#                 "suspicion_score":   score_data["suspicion_score"],
#                 "events":            score_data["events"],
#             }))
#
#         # Step 5 — draw HUD on screen
#         if SHOW_WINDOW:
#             frame = draw_hud(frame, face_count, direction,
#                              yaw, pitch, score_data)
#             cv2.imshow("AI Proctor — Phase 1   [Q to quit]", frame)
#
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 print("\nStopped by user.")
#                 break
#
#     cap.release()
#     cv2.destroyAllWindows()
#     print(json.dumps({"status": "session_ended"}))
#
#
# if __name__ == "__main__":
#     main()


# ================================================================
#  main.py  — Phase 2 version
#  JOB: Opens webcam, runs ALL detectors, prints JSON.
#       Now includes phone detection via YOLOv8.
#
#  HOW TO RUN:  python main.py
#  QUIT:        Press Q in the webcam window
# ================================================================

import cv2
import json
import time

from face_detection  import count_faces
from head_pose       import get_head_pose
from phone_detection import detect_phone       # NEW in Phase 2
from scorer          import SuspicionScorer

# ── Settings ─────────────────────────────────────────────────────
CAMERA_INDEX     = 0
JSON_PRINT_EVERY = 0.5
SHOW_WINDOW      = True
# ─────────────────────────────────────────────────────────────────


def draw_hud(frame, face_count, direction, yaw, pitch,
             phone_detected, score_data):
    """Draw info panel on the webcam window."""

    score = score_data["suspicion_score"]

    cv2.rectangle(frame, (0, 0), (380, 158), (15, 15, 15), -1)

    bar_color = (80, 200, 80) if score == 0 else \
                (0, 165, 255) if score < 50 else \
                (60, 60, 220)

    cv2.putText(frame, f"Faces  : {face_count}",
                (10, 26),  cv2.FONT_HERSHEY_SIMPLEX, 0.62, (220,220,220), 1)
    cv2.putText(frame, f"Gaze   : {direction}",
                (10, 52),  cv2.FONT_HERSHEY_SIMPLEX, 0.62, (220,220,220), 1)
    cv2.putText(frame, f"Phone  : {'YES !!!' if phone_detected else 'no'}",
                (10, 78),  cv2.FONT_HERSHEY_SIMPLEX, 0.62,
                (0,0,255) if phone_detected else (220,220,220), 1)

    if yaw is not None:
        cv2.putText(frame, f"Yaw: {yaw:+.1f}   Pitch: {pitch:+.1f}",
                    (10, 104), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (150,150,150), 1)

    secs = score_data["look_away_secs"]
    if secs > 0:
        cv2.putText(frame, f"Away: {secs:.1f}s",
                    (10, 126), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (100,180,255), 1)

    # Score bar
    cv2.rectangle(frame, (10, 134), (355, 150), (50,50,50), -1)
    bw = int(345 * score / 100)
    if bw > 0:
        cv2.rectangle(frame, (10, 134), (10 + bw, 150), bar_color, -1)
    cv2.putText(frame, f"{score}/100",
                (360, 149), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200,200,200), 1)

    if score_data["is_suspicious"]:
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0,0), (w-1, h-1), (0,0,200), 3)

    return frame


def main():
    print("=" * 50)
    print("  AI Proctoring System — Phase 2")
    print("  Face + Gaze + Phone Detection")
    print("  Press Q in the video window to quit")
    print("=" * 50)
    print()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(json.dumps({"error": f"Cannot open camera {CAMERA_INDEX}"}))
        return

    print("Camera opened. Starting detection...\n")

    scorer     = SuspicionScorer()
    last_print = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(json.dumps({"error": "Lost camera connection"}))
            break

        # Step 1 — count faces
        face_count, frame = count_faces(frame)

        # Step 2 — gaze direction
        direction, yaw, pitch, frame = get_head_pose(frame)

        # Step 3 — phone detection (NEW)
        phone_detected, frame = detect_phone(frame)

        # Step 4 — suspicion score
        score_data = scorer.update(face_count, direction, phone_detected)

        now = time.time()

        # Step 5 — print JSON
        if now - last_print >= JSON_PRINT_EVERY:
            last_print = now
            print(json.dumps({
                "timestamp":         round(now, 3),
                "face_count":        face_count,
                "looking_direction": direction,
                "yaw_deg":           yaw,
                "pitch_deg":         pitch,
                "phone_detected":    phone_detected,
                "look_away_secs":    score_data["look_away_secs"],
                "suspicion_score":   score_data["suspicion_score"],
                "events":            score_data["events"],
            }))

        # Step 6 — draw HUD
        if SHOW_WINDOW:
            frame = draw_hud(frame, face_count, direction,
                             yaw, pitch, phone_detected, score_data)
            cv2.imshow("AI Proctor — Phase 2   [Q to quit]", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nStopped.")
                break

    cap.release()
    cv2.destroyAllWindows()
    print(json.dumps({"status": "session_ended"}))


if __name__ == "__main__":
    main()




# # 📁 backend/ — brand new folder
#
#
#
# ## 📄 backend/requirements.txt (NEW FILE)
#
# fastapi==0.111.0
# uvicorn==0.30.1
# websockets==12.0
# python-multipart==0.0.9
# opencv-python==4.9.0.80
# mediapipe==0.10.14
# numpy==1.26.4
# ultralytics==8.2.0