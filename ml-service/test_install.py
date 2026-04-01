# ================================================================
#  test_install.py
#  JOB: Verify all libraries installed correctly.
#  RUN THIS BEFORE main.py.
#
#  HOW TO RUN:  python test_install.py
# ================================================================

import sys

print("=" * 50)
print("  Phase 1 — Installation Check")
print("=" * 50)

# Check Python version
print(f"\nPython: {sys.version}")
major, minor = sys.version_info[:2]
if major == 3 and 8 <= minor <= 11:
    print("  [OK] Python version compatible")
else:
    print(f"  [!!] Python {major}.{minor} may NOT work with MediaPipe")
    print("       Install Python 3.10 from: https://python.org")

# Check OpenCV
print("\nChecking opencv-python ...")
try:
    import cv2
    print(f"  [OK] version: {cv2.__version__}")
except ImportError:
    print("  [FAIL] not installed — run: pip install opencv-python==4.9.0.80")

# Check MediaPipe
print("\nChecking mediapipe ...")
try:
    import mediapipe as mp
    print(f"  [OK] version: {mp.__version__}")
    _ = mp.solutions.face_detection
    _ = mp.solutions.face_mesh
    print("  [OK] face_detection loaded")
    print("  [OK] face_mesh loaded")
except ImportError:
    print("  [FAIL] not installed — run: pip install mediapipe==0.10.14")
except Exception as e:
    print(f"  [FAIL] error: {e}")

# Check NumPy
print("\nChecking numpy ...")
try:
    import numpy as np
    print(f"  [OK] version: {np.__version__}")
except ImportError:
    print("  [FAIL] not installed — run: pip install numpy==1.26.4")

# Check camera
print("\nChecking camera ...")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        h, w = frame.shape[:2]
        print(f"  [OK] Camera 0 works — resolution: {w}x{h}")
        cap.release()
    else:
        print("  [WARN] Camera 0 not found")
        print("         Check permissions or plug in your webcam")
except Exception as e:
    print(f"  [WARN] {e}")

print("\n" + "=" * 50)
print("  All [OK]? Run:  python main.py")
print("=" * 50)