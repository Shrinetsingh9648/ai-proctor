# ================================================================
#  head_pose.py
#  JOB: Detect which direction the student is looking.
#  RETURNS: "centered" / "looking_left" / "looking_right" /
#           "looking_up" / "looking_down" / "no_face"
#  CALLED BY: main.py
# ================================================================

import cv2
import mediapipe as mp
import numpy as np

# --- Create Face Mesh detector ONCE -----------------------------
# Face Mesh finds 468 tiny dot landmarks on a face
mp_face_mesh = mp.solutions.face_mesh
mp_drawing   = mp.solutions.drawing_utils
mp_styles    = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,               # track only 1 face for pose
    refine_landmarks=True,         # more accurate eye landmarks
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ----------------------------------------------------------------
# 3D face model — real-world positions (in mm) of 6 key points
# on a generic human face. Used for the PnP maths below.
# ----------------------------------------------------------------
FACE_3D_MODEL = np.array([
    [  0.0,    0.0,   0.0 ],   # Nose tip           → landmark 1
    [  0.0,  -63.6, -12.5 ],   # Chin               → landmark 152
    [-43.3,   32.7, -26.0 ],   # Left eye corner    → landmark 263
    [ 43.3,   32.7, -26.0 ],   # Right eye corner   → landmark 33
    [-28.9,  -28.9, -24.1 ],   # Left mouth corner  → landmark 287
    [ 28.9,  -28.9, -24.1 ],   # Right mouth corner → landmark 57
], dtype=np.float64)

LANDMARK_IDS = [1, 152, 263, 33, 287, 57]  # which landmarks to extract

# ----------------------------------------------------------------
# Thresholds — how many degrees = "looking away"
# Increase if you get too many false alarms.
# Decrease for stricter detection.
# ----------------------------------------------------------------
YAW_LIMIT   = 20    # degrees left or right
PITCH_LIMIT = 20    # degrees up or down


def get_head_pose(frame):
    """
    INPUT  : frame — one webcam image (numpy array, BGR)
    OUTPUT : direction   — string like "looking_left"
             yaw_deg     — left/right angle in degrees  (+ = right)
             pitch_deg   — up/down angle in degrees     (+ = down)
             frame       — image with face mesh dots drawn on it
    """

    h, w = frame.shape[:2]   # frame height and width in pixels

    # Convert BGR → RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False          # tiny speed trick

    results = face_mesh.process(rgb)

    rgb.flags.writeable = True

    # No face found → return early
    if not results.multi_face_landmarks:
        return "no_face", None, None, frame

    # Use the first (primary) face
    face_landmarks = results.multi_face_landmarks[0]

    # Draw the mesh dots on screen
    mp_drawing.draw_landmarks(
        image=frame,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_styles.get_default_face_mesh_contours_style()
    )

    # --- Pull out the 6 key landmark positions as 2D pixel coords ---
    points_2d = []
    for lid in LANDMARK_IDS:
        lm = face_landmarks.landmark[lid]
        points_2d.append([int(lm.x * w), int(lm.y * h)])
    points_2d = np.array(points_2d, dtype=np.float64)

    # --- Build camera matrix (approximate, no calibration needed) ---
    focal     = float(w)
    cx, cy    = w / 2.0, h / 2.0
    cam_mat   = np.array([
        [focal, 0,     cx],
        [0,     focal, cy],
        [0,     0,     1 ]
    ], dtype=np.float64)
    dist      = np.zeros((4, 1))   # assume no lens distortion

    # --- solvePnP: find the head rotation that maps 3D model → 2D dots ---
    # This is a standard computer vision algorithm built into OpenCV.
    # It answers: "what rotation of a 3D face produces these 2D landmark dots?"
    ok, rvec, tvec = cv2.solvePnP(
        FACE_3D_MODEL, points_2d, cam_mat, dist,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not ok:
        return "unknown", None, None, frame

    # --- Convert rotation vector → matrix → yaw and pitch angles ---
    rmat, _ = cv2.Rodrigues(rvec)
    sy = np.sqrt(rmat[0, 0]**2 + rmat[1, 0]**2)

    if sy > 1e-6:
        pitch = np.arctan2(-rmat[2, 0], sy)
        yaw   = np.arctan2( rmat[2, 1], rmat[2, 2])
    else:                          # gimbal lock (very rare edge case)
        pitch = np.arctan2(-rmat[2, 0], sy)
        yaw   = 0.0

    yaw_deg   = float(np.degrees(yaw))
    pitch_deg = float(np.degrees(pitch))

    direction = _classify(yaw_deg, pitch_deg)

    return direction, round(yaw_deg, 1), round(pitch_deg, 1), frame


def _classify(yaw, pitch):
    """ Convert yaw + pitch angles into a direction string. """
    if abs(yaw) <= YAW_LIMIT and abs(pitch) <= PITCH_LIMIT:
        return "centered"
    if abs(yaw) >= abs(pitch):
        return "looking_left"  if yaw   < 0 else "looking_right"
    else:
        return "looking_up"    if pitch < 0 else "looking_down"