# # ================================================================
# #  scorer.py
# #  JOB: Combine face_count + direction into ONE suspicion score.
# #       Score: 0 = all clear,  100 = very suspicious
# #  CALLED BY: main.py
# # ================================================================
#
# import time
#
# # --- Point values ---
# POINTS_LOOKING_AWAY   = 20   # only added after 3 continuous seconds away
# POINTS_MULTIPLE_FACES = 40   # instant — 2 faces is always suspicious
# POINTS_NO_FACE        = 30   # face disappeared
# MAX_SCORE             = 100
#
# LOOK_AWAY_HOLD_SECONDS = 3.0  # ignore glances shorter than this
#
#
# class SuspicionScorer:
#     """
#     We use a class (not just a function) because we need to
#     REMEMBER things between frames — like when looking-away started.
#     """
#
#     def __init__(self):
#         self.look_away_start = None   # timestamp when looking away began
#         self.look_away_secs  = 0.0   # total continuous seconds looking away
#
#     def update(self, face_count, direction):
#         """
#         Call once per frame with the latest detection values.
#
#         INPUT  : face_count — int    (0, 1, 2 ...)
#                  direction  — string ("centered", "looking_left", etc.)
#         OUTPUT : dict with score, events, and timing info
#         """
#         now    = time.time()
#         score  = 0
#         events = []
#
#         # Rule 1 — No face visible
#         if face_count == 0 or direction == "no_face":
#             score += POINTS_NO_FACE
#             events.append("no_face")
#             self.look_away_start = None   # reset look-away timer
#             self.look_away_secs  = 0.0
#
#         # Rule 2 — Multiple faces
#         elif face_count > 1:
#             score += POINTS_MULTIPLE_FACES
#             events.append("multiple_faces")
#             self.look_away_start = None
#             self.look_away_secs  = 0.0
#
#         # Rule 3 — Looking away from screen
#         elif direction in ("looking_left", "looking_right",
#                            "looking_up",   "looking_down"):
#             if self.look_away_start is None:
#                 self.look_away_start = now          # start the timer
#
#             self.look_away_secs = now - self.look_away_start
#
#             if self.look_away_secs >= LOOK_AWAY_HOLD_SECONDS:
#                 score += POINTS_LOOKING_AWAY        # only flag after 3s
#                 events.append("looking_away")
#
#         # Rule 4 — All clear
#         else:
#             self.look_away_start = None             # reset timer
#             self.look_away_secs  = 0.0
#
#         return {
#             "suspicion_score":  min(score, MAX_SCORE),
#             "events":           events,
#             "look_away_secs":   round(self.look_away_secs, 1),
#             "is_suspicious":    score > 0,
#         }



# ================================================================
#  scorer.py
#  JOB: Combine ALL signals into one suspicion score 0–100.
#       Updated for Phase 2: now includes phone_detected.
#  CALLED BY: main.py
# ================================================================

import time

# --- Point values ---
POINTS_LOOKING_AWAY   = 20   # after 3 continuous seconds looking away
POINTS_MULTIPLE_FACES = 40   # instant
POINTS_NO_FACE        = 30   # instant
POINTS_PHONE          = 50   # instant — phone is a hard flag
MAX_SCORE             = 100

LOOK_AWAY_HOLD_SECONDS = 3.0


class SuspicionScorer:

    def __init__(self):
        self.look_away_start = None
        self.look_away_secs  = 0.0

    def update(self, face_count, direction, phone_detected=False):
        """
        INPUT  : face_count     — int
                 direction      — string
                 phone_detected — bool (NEW in Phase 2)
        OUTPUT : dict with score, events, timing
        """
        now    = time.time()
        score  = 0
        events = []

        # Rule 1 — Phone visible (highest priority flag)
        if phone_detected:
            score += POINTS_PHONE
            events.append("phone_detected")

        # Rule 2 — No face
        if face_count == 0 or direction == "no_face":
            score += POINTS_NO_FACE
            events.append("no_face")
            self.look_away_start = None
            self.look_away_secs  = 0.0

        # Rule 3 — Multiple faces
        elif face_count > 1:
            score += POINTS_MULTIPLE_FACES
            events.append("multiple_faces")
            self.look_away_start = None
            self.look_away_secs  = 0.0

        # Rule 4 — Looking away
        elif direction in ("looking_left", "looking_right",
                           "looking_up",   "looking_down"):
            if self.look_away_start is None:
                self.look_away_start = now
            self.look_away_secs = now - self.look_away_start

            if self.look_away_secs >= LOOK_AWAY_HOLD_SECONDS:
                score += POINTS_LOOKING_AWAY
                events.append("looking_away")

        # Rule 5 — All clear
        else:
            self.look_away_start = None
            self.look_away_secs  = 0.0

        return {
            "suspicion_score": min(score, MAX_SCORE),
            "events":          events,
            "look_away_secs":  round(self.look_away_secs, 1),
            "is_suspicious":   score > 0,
        }