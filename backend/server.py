# # # ================================================================
# # #  server.py
# # #  JOB: FastAPI server with two endpoints:
# # #
# # #    GET  /              → health check (just says "server is alive")
# # #    WS   /ws/proctor    → WebSocket — browser sends frames,
# # #                          server runs AI and sends back JSON
# # #
# # #  HOW TO RUN:
# # #    cd backend
# # #    python -m venv venv
# # #    venv\Scripts\activate
# # #    pip install -r requirements.txt
# # #    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
# # #
# # #  THEN OPEN IN BROWSER:
# # #    http://localhost:8000
# # # ================================================================
# #
# # import cv2
# # import json
# # import base64
# # import numpy as np
# # import sys
# # import os
# #
# # from fastapi            import FastAPI, WebSocket, WebSocketDisconnect
# # from fastapi.responses  import HTMLResponse
# #
# # # --- Add ml-service to Python path so we can import our modules ---
# # # This lets backend/server.py use face_detection.py, head_pose.py, etc.
# # ML_SERVICE_PATH = os.path.join(os.path.dirname(__file__), "..", "ml-service")
# # sys.path.append(os.path.abspath(ML_SERVICE_PATH))
# #
# # from face_detection  import count_faces
# # from head_pose       import get_head_pose
# # from phone_detection import detect_phone
# # from scorer          import SuspicionScorer
# #
# # # ── Create FastAPI app ────────────────────────────────────────────
# # app = FastAPI(title="AI Proctor — Phase 2 Backend")
# #
# #
# # # ── Health check endpoint ─────────────────────────────────────────
# # @app.get("/")
# # def root():
# #     """
# #     Visit http://localhost:8000 in your browser.
# #     If you see this JSON, the server is running correctly.
# #     """
# #     return {"status": "AI Proctor backend is running"}
# #
# #
# # # ── Test page — browser webcam → WebSocket demo ──────────────────
# # @app.get("/test", response_class=HTMLResponse)
# # def test_page():
# #     """
# #     Visit http://localhost:8000/test
# #     A simple browser page that captures your webcam and
# #     sends frames to the WebSocket, then shows the JSON response.
# #     This is your Phase 4 frontend in its simplest possible form.
# #     """
# #     return HTMLResponse(content="""
# # <!DOCTYPE html>
# # <html>
# # <head>
# #   <title>AI Proctor — Test Page</title>
# #   <style>
# #     body { font-family: monospace; background: #111; color: #eee; padding: 20px; }
# #     h2   { color: #7af; }
# #     video, canvas { border: 1px solid #444; border-radius: 6px; }
# #     #output { background: #1a1a1a; padding: 12px; border-radius: 6px;
# #               margin-top: 12px; white-space: pre; font-size: 13px;
# #               min-height: 80px; color: #8f8; }
# #     .alert { color: #f66 !important; }
# #   </style>
# # </head>
# # <body>
# #   <h2>AI Proctor — WebSocket Test</h2>
# #
# #   <video id="video" width="480" height="360" autoplay></video>
# #   <canvas id="canvas" width="480" height="360" style="display:none"></canvas>
# #
# #   <div id="output">Connecting to WebSocket...</div>
# #
# #   <script>
# #     const video   = document.getElementById('video');
# #     const canvas  = document.getElementById('canvas');
# #     const output  = document.getElementById('output');
# #     const ctx     = canvas.getContext('2d');
# #
# #     // Open webcam
# #     navigator.mediaDevices.getUserMedia({ video: true })
# #       .then(stream => { video.srcObject = stream; })
# #       .catch(e => { output.textContent = 'Camera error: ' + e; });
# #
# #     // Connect to WebSocket
# #     const ws = new WebSocket('ws://localhost:8000/ws/proctor');
# #
# #     ws.onopen = () => {
# #       output.textContent = 'Connected! Sending frames...';
# #       sendFrame();   // start sending
# #     };
# #
# #     ws.onmessage = (event) => {
# #       const data = JSON.parse(event.data);
# #       const text = JSON.stringify(data, null, 2);
# #       output.textContent = text;
# #       output.className   = data.suspicion_score > 0 ? 'alert' : '';
# #     };
# #
# #     ws.onerror = (e) => {
# #       output.textContent = 'WebSocket error. Is the server running?';
# #     };
# #
# #     ws.onclose = () => {
# #       output.textContent = 'WebSocket closed.';
# #     };
# #
# #     // Capture one frame from webcam → send as base64 JPEG → repeat
# #     function sendFrame() {
# #       if (ws.readyState !== WebSocket.OPEN) return;
# #
# #       ctx.drawImage(video, 0, 0, 480, 360);
# #
# #       // Convert canvas to base64 JPEG (quality 0.7 = good balance)
# #       const base64 = canvas.toDataURL('image/jpeg', 0.7);
# #
# #       ws.send(base64);
# #
# #       // Send next frame in 500ms (2 frames per second)
# #       // Increase frequency later — 500ms is safe for development
# #       setTimeout(sendFrame, 500);
# #     }
# #   </script>
# # </body>
# # </html>
# #     """)
# #
# #
# # # ── WebSocket endpoint ────────────────────────────────────────────
# # @app.websocket("/ws/proctor")
# # async def proctor_websocket(websocket: WebSocket):
# #     """
# #     This is the main endpoint the React frontend will connect to.
# #
# #     PROTOCOL:
# #       Browser → Server : base64-encoded JPEG image (one frame)
# #       Server → Browser : JSON string with detection results
# #     """
# #     await websocket.accept()
# #     print("WebSocket client connected")
# #
# #     # Each connected student gets their own scorer (tracks their state)
# #     scorer = SuspicionScorer()
# #
# #     try:
# #         while True:
# #             # 1. Receive a base64 frame from the browser
# #             raw = await websocket.receive_text()
# #
# #             # 2. Decode base64 → numpy image array
# #             # Browser sends: "data:image/jpeg;base64,/9j/4AAQ..."
# #             # We strip the header and decode the rest
# #             if "," in raw:
# #                 raw = raw.split(",")[1]
# #
# #             img_bytes = base64.b64decode(raw)
# #             np_arr    = np.frombuffer(img_bytes, dtype=np.uint8)
# #             frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
# #
# #             if frame is None:
# #                 await websocket.send_text(
# #                     json.dumps({"error": "Could not decode frame"})
# #                 )
# #                 continue
# #
# #             # 3. Run all three detectors
# #             face_count,    frame = count_faces(frame)
# #             direction, yaw, pitch, frame = get_head_pose(frame)
# #             phone_detected, frame = detect_phone(frame)
# #
# #             # 4. Update suspicion score
# #             score_data = scorer.update(face_count, direction, phone_detected)
# #
# #             # 5. Build response JSON and send back to browser
# #             response = {
# #                 "face_count":        face_count,
# #                 "looking_direction": direction,
# #                 "yaw_deg":           yaw,
# #                 "pitch_deg":         pitch,
# #                 "phone_detected":    phone_detected,
# #                 "look_away_secs":    score_data["look_away_secs"],
# #                 "suspicion_score":   score_data["suspicion_score"],
# #                 "events":            score_data["events"],
# #             }
# #
# #             await websocket.send_text(json.dumps(response))
# #
# #     except WebSocketDisconnect:
# #         print("Client disconnected")
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         await websocket.close()
#
#
#
# # import cv2
# # import json
# # import base64
# # import numpy as np
# # import sys
# # import os
# # import asyncpg
# # from datetime import datetime
# #
# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # from fastapi.responses import HTMLResponse, JSONResponse
# #
# # ML_SERVICE_PATH = os.path.join(os.path.dirname(__file__), "..", "ml-service")
# # sys.path.append(os.path.abspath(ML_SERVICE_PATH))
# #
# # from face_detection  import count_faces
# # from head_pose       import get_head_pose
# # from phone_detection import detect_phone
# # from scorer          import SuspicionScorer
# #
# # # ── Database config ───────────────────────────────────────────────
# # DB_CONFIG = {
# #     "host":     "localhost",
# #     "port":     5432,
# #     "database": "proctor_db",
# #     "user":     "postgres",
# #     "password": "shrinetsingh@9648",
# # }
# #
# # # app = FastAPI(title="AI Proctor — Phase 4")
# # from fastapi.middleware.cors import CORSMiddleware
# #
# # app = FastAPI(title="AI Proctor — Phase 4")
# #
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["http://localhost:3000"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# #
# # # DB connection pool (created on startup)
# # db_pool = None
# #
# # @app.on_event("startup")
# # async def startup():
# #     global db_pool
# #     try:
# #         db_pool = await asyncpg.create_pool(**DB_CONFIG)
# #         print("Database connected successfully")
# #     except Exception as e:
# #         print(f"Database connection failed: {e}")
# #         db_pool = None
# #
# # @app.on_event("shutdown")
# # async def shutdown():
# #     if db_pool:
# #         await db_pool.close()
# #
# #
# # async def save_log(user_id: str, event: str, score: int):
# #     """Save one suspicious event to the database."""
# #     if not db_pool:
# #         return
# #     try:
# #         async with db_pool.acquire() as conn:
# #             await conn.execute(
# #                 """INSERT INTO session_logs (user_id, event, suspicion_score)
# #                    VALUES ($1, $2, $3)""",
# #                 user_id, event, score
# #             )
# #     except Exception as e:
# #         print(f"DB write error: {e}")
# #
# #
# # @app.get("/")
# # def root():
# #     return {"status": "AI Proctor backend is running — Phase 4"}
# #
# #
# # @app.get("/logs")
# # async def get_logs():
# #     """Return all session logs — admin will use this."""
# #     if not db_pool:
# #         return JSONResponse({"error": "Database not connected"}, status_code=500)
# #     async with db_pool.acquire() as conn:
# #         rows = await conn.fetch(
# #             "SELECT * FROM session_logs ORDER BY timestamp DESC LIMIT 100"
# #         )
# #     return [dict(r) for r in rows]
# #
# #
# # @app.get("/logs/{user_id}")
# # async def get_logs_by_user(user_id: str):
# #     """Return logs for one specific student."""
# #     if not db_pool:
# #         return JSONResponse({"error": "Database not connected"}, status_code=500)
# #     async with db_pool.acquire() as conn:
# #         rows = await conn.fetch(
# #             "SELECT * FROM session_logs WHERE user_id=$1 ORDER BY timestamp DESC",
# #             user_id
# #         )
# #     return [dict(r) for r in rows]
# #
# #
# # @app.websocket("/ws/proctor")
# # async def proctor_websocket(websocket: WebSocket):
# #     await websocket.accept()
# #     print("Client connected")
# #
# #     scorer  = SuspicionScorer()
# #     user_id = "student_001"   # Phase 5 will use real login
# #
# #     try:
# #         while True:
# #             raw = await websocket.receive_text()
# #
# #             if "," in raw:
# #                 raw = raw.split(",")[1]
# #
# #             img_bytes = base64.b64decode(raw)
# #             np_arr    = np.frombuffer(img_bytes, dtype=np.uint8)
# #             frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
# #
# #             if frame is None:
# #                 await websocket.send_text(json.dumps({"error": "Bad frame"}))
# #                 continue
# #
# #             face_count,             frame = count_faces(frame)
# #             direction, yaw, pitch,  frame = get_head_pose(frame)
# #             phone_detected,         frame = detect_phone(frame)
# #
# #             score_data = scorer.update(face_count, direction, phone_detected)
# #
# #             # Save each event to database
# #             for event in score_data["events"]:
# #                 await save_log(user_id, event, score_data["suspicion_score"])
# #
# #             response = {
# #                 "face_count":        face_count,
# #                 "looking_direction": direction,
# #                 "yaw_deg":           yaw,
# #                 "pitch_deg":         pitch,
# #                 "phone_detected":    phone_detected,
# #                 "look_away_secs":    score_data["look_away_secs"],
# #                 "suspicion_score":   score_data["suspicion_score"],
# #                 "events":            score_data["events"],
# #             }
# #
# #             await websocket.send_text(json.dumps(response))
# #
# #     except WebSocketDisconnect:
# #         print("Client disconnected")
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         await websocket.close()
#
#
# # import cv2
# # import json
# # import base64
# # import numpy as np
# # import sys
# # import os
# # import asyncpg
# # from datetime import datetime, timedelta
# # from typing import Optional
# #
# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
# # from fastapi.responses import JSONResponse
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# # from pydantic import BaseModel
# # from jose import JWTError, jwt
# # from passlib.context import CryptContext
# #
# # ML_SERVICE_PATH = os.path.join(os.path.dirname(__file__), "..", "ml-service")
# # sys.path.append(os.path.abspath(ML_SERVICE_PATH))
# #
# # from face_detection  import count_faces
# # from head_pose       import get_head_pose
# # from phone_detection import detect_phone
# # from scorer          import SuspicionScorer
# #
# # # ── Security config ───────────────────────────────────────────────
# # SECRET_KEY  = "your-secret-key-change-in-production"
# # ALGORITHM   = "HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES = 60
# #
# # pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
# # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# #
# # # ── Database config ───────────────────────────────────────────────
# # DB_CONFIG = {
# #     "host":     "localhost",
# #     "port":     5432,
# #     "database": "proctor_db",
# #     "user":     "postgres",
# #     "password": "shrinetsingh@9648",   # change if yours is different
# # }
# #
# # # ── Pydantic models ───────────────────────────────────────────────
# # class Token(BaseModel):
# #     access_token: str
# #     token_type:   str
# #     role:         str
# #     username:     str
# #
# # class UserCreate(BaseModel):
# #     username: str
# #     password: str
# #     role:     str = "student"
# #
# # # ── FastAPI app ───────────────────────────────────────────────────
# # app = FastAPI(title="AI Proctor — Phase 6")
# #
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["http://localhost:3000"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# #
# # db_pool = None
# #
# # @app.on_event("startup")
# # async def startup():
# #     global db_pool
# #     try:
# #         db_pool = await asyncpg.create_pool(**DB_CONFIG)
# #         print("Database connected successfully")
# #     except Exception as e:
# #         print(f"Database connection failed: {e}")
# #         db_pool = None
# #
# # @app.on_event("shutdown")
# # async def shutdown():
# #     if db_pool:
# #         await db_pool.close()
# #
# # # ── Auth helpers ──────────────────────────────────────────────────
# # def verify_password(plain, hashed):
# #     return pwd_context.verify(plain, hashed)
# #
# # def create_access_token(data: dict):
# #     to_encode = data.copy()
# #     expire    = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
# #     to_encode.update({"exp": expire})
# #     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# #
# # async def get_user(username: str):
# #     async with db_pool.acquire() as conn:
# #         return await conn.fetchrow(
# #             "SELECT * FROM users WHERE username=$1", username
# #         )
# #
# # async def get_current_user(token: str = Depends(oauth2_scheme)):
# #     try:
# #         payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         username = payload.get("sub")
# #         if not username:
# #             raise HTTPException(status_code=401, detail="Invalid token")
# #     except JWTError:
# #         raise HTTPException(status_code=401, detail="Invalid token")
# #     user = await get_user(username)
# #     if not user:
# #         raise HTTPException(status_code=401, detail="User not found")
# #     return dict(user)
# #
# # # ── Auth endpoints ────────────────────────────────────────────────
# # @app.post("/login", response_model=Token)
# # async def login(form_data: OAuth2PasswordRequestForm = Depends()):
# #     user = await get_user(form_data.username)
# #     if not user or not verify_password(form_data.password, user["password_hash"]):
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect username or password",
# #         )
# #     token = create_access_token({"sub": user["username"], "role": user["role"]})
# #     return {
# #         "access_token": token,
# #         "token_type":   "bearer",
# #         "role":         user["role"],
# #         "username":     user["username"],
# #     }
# #
# # @app.post("/register")
# # async def register(user: UserCreate):
# #     hashed = pwd_context.hash(user.password)
# #     try:
# #         async with db_pool.acquire() as conn:
# #             await conn.execute(
# #                 "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3)",
# #                 user.username, hashed, user.role
# #             )
# #         return {"message": f"User {user.username} created successfully"}
# #     except Exception:
# #         raise HTTPException(status_code=400, detail="Username already exists")
# #
# # @app.get("/me")
# # async def get_me(current_user=Depends(get_current_user)):
# #     return {"username": current_user["username"], "role": current_user["role"]}
# #
# # # ── Logs endpoints ────────────────────────────────────────────────
# # async def save_log(user_id: str, event: str, score: int):
# #     if not db_pool:
# #         return
# #     try:
# #         async with db_pool.acquire() as conn:
# #             await conn.execute(
# #                 "INSERT INTO session_logs (user_id, event, suspicion_score) VALUES ($1, $2, $3)",
# #                 user_id, event, score
# #             )
# #     except Exception as e:
# #         print(f"DB write error: {e}")
# #
# # @app.get("/logs")
# # async def get_logs(current_user=Depends(get_current_user)):
# #     if current_user["role"] != "admin":
# #         raise HTTPException(status_code=403, detail="Admin only")
# #     async with db_pool.acquire() as conn:
# #         rows = await conn.fetch(
# #             "SELECT * FROM session_logs ORDER BY timestamp DESC LIMIT 100"
# #         )
# #     return [dict(r) for r in rows]
# #
# # @app.get("/my-logs")
# # async def get_my_logs(current_user=Depends(get_current_user)):
# #     async with db_pool.acquire() as conn:
# #         rows = await conn.fetch(
# #             "SELECT * FROM session_logs WHERE user_id=$1 ORDER BY timestamp DESC",
# #             current_user["username"]
# #         )
# #     return [dict(r) for r in rows]
# #
# # # ── WebSocket ─────────────────────────────────────────────────────
# # @app.websocket("/ws/proctor")
# # async def proctor_websocket(websocket: WebSocket):
# #     await websocket.accept()
# #
# #     # Get token from query param: ws://localhost:8000/ws/proctor?token=xxx
# #     token    = websocket.query_params.get("token", "")
# #     username = "anonymous"
# #
# #     try:
# #         payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         username = payload.get("sub", "anonymous")
# #     except Exception:
# #         pass
# #
# #     print(f"Client connected: {username}")
# #     scorer = SuspicionScorer()
# #
# #     try:
# #         while True:
# #             raw = await websocket.receive_text()
# #             if "," in raw:
# #                 raw = raw.split(",")[1]
# #
# #             img_bytes = base64.b64decode(raw)
# #             np_arr    = np.frombuffer(img_bytes, dtype=np.uint8)
# #             frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
# #
# #             if frame is None:
# #                 await websocket.send_text(json.dumps({"error": "Bad frame"}))
# #                 continue
# #
# #             face_count,            frame = count_faces(frame)
# #             direction, yaw, pitch, frame = get_head_pose(frame)
# #             phone_detected,        frame = detect_phone(frame)
# #             score_data = scorer.update(face_count, direction, phone_detected)
# #
# #             for event in score_data["events"]:
# #                 await save_log(username, event, score_data["suspicion_score"])
# #
# #             await websocket.send_text(json.dumps({
# #                 "face_count":        face_count,
# #                 "looking_direction": direction,
# #                 "yaw_deg":           yaw,
# #                 "pitch_deg":         pitch,
# #                 "phone_detected":    phone_detected,
# #                 "look_away_secs":    score_data["look_away_secs"],
# #                 "suspicion_score":   score_data["suspicion_score"],
# #                 "events":            score_data["events"],
# #             }))
# #
# #     except WebSocketDisconnect:
# #         print(f"Client disconnected: {username}")
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         await websocket.close()
#
#
#
#
# import cv2
# import json
# import base64
# import numpy as np
# import sys
# import os
# import asyncpg
# import bcrypt as _bcrypt
# from datetime import datetime, timedelta
# from typing import Optional
#
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from jose import JWTError, jwt
#
# ML_SERVICE_PATH = os.path.join(os.path.dirname(__file__), "..", "ml-service")
# sys.path.append(os.path.abspath(ML_SERVICE_PATH))
#
# from face_detection  import count_faces
# from head_pose       import get_head_pose
# from phone_detection import detect_phone
# from scorer          import SuspicionScorer
#
# # ── Security config ───────────────────────────────────────────────
# SECRET_KEY  = "your-secret-key-change-in-production"
# ALGORITHM   = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#
# # ── Database config ───────────────────────────────────────────────
# # DB_CONFIG = {
# #     "host":     "localhost",
# #     "port":     5432,
# #     "database": "proctor_db",
# #     "user":     "postgres",
# #     "password": "shrinetsingh@9648",
# # }
#
#
# import os
#
# DATABASE_URL = os.environ.get(
#     "DATABASE_URL",
#     "postgresql://postgres:shrinetsingh@9648@localhost:5432/proctor_db"
# )
#
# @app.on_event("startup")
# async def startup():
#     global db_pool
#     try:
#         db_pool = await asyncpg.create_pool(DATABASE_URL)
#         print("Database connected successfully")
#     except Exception as e:
#         print(f"Database connection failed: {e}")
#         db_pool = None
#
# # ── Pydantic models ───────────────────────────────────────────────
# class Token(BaseModel):
#     access_token: str
#     token_type:   str
#     role:         str
#     username:     str
#
# class UserCreate(BaseModel):
#     username: str
#     password: str
#     role:     str = "student"
#
# # ── FastAPI app ───────────────────────────────────────────────────
# app = FastAPI(title="AI Proctor — Phase 6")
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# db_pool = None
#
# @app.on_event("startup")
# async def startup():
#     global db_pool
#     try:
#         db_pool = await asyncpg.create_pool(**DB_CONFIG)
#         print("Database connected successfully")
#     except Exception as e:
#         print(f"Database connection failed: {e}")
#         db_pool = None
#
# @app.on_event("shutdown")
# async def shutdown():
#     if db_pool:
#         await db_pool.close()
#
# # ── Auth helpers ──────────────────────────────────────────────────
# def verify_password(plain, hashed):
#     return _bcrypt.checkpw(plain.encode(), hashed.encode())
#
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire    = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#
# async def get_user(username: str):
#     async with db_pool.acquire() as conn:
#         return await conn.fetchrow(
#             "SELECT * FROM users WHERE username=$1", username
#         )
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if not username:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     user = await get_user(username)
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return dict(user)
#
# # ── Auth endpoints ────────────────────────────────────────────────
# @app.post("/login", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = await get_user(form_data.username)
#     if not user or not verify_password(form_data.password, user["password_hash"]):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#         )
#     token = create_access_token({"sub": user["username"], "role": user["role"]})
#     return {
#         "access_token": token,
#         "token_type":   "bearer",
#         "role":         user["role"],
#         "username":     user["username"],
#     }
#
# @app.post("/register")
# async def register(user: UserCreate):
#     hashed = _bcrypt.hashpw(user.password.encode(), _bcrypt.gensalt()).decode()
#     try:
#         async with db_pool.acquire() as conn:
#             await conn.execute(
#                 "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3)",
#                 user.username, hashed, user.role
#             )
#         return {"message": f"User {user.username} created successfully"}
#     except Exception:
#         raise HTTPException(status_code=400, detail="Username already exists")
#
# @app.get("/me")
# async def get_me(current_user=Depends(get_current_user)):
#     return {"username": current_user["username"], "role": current_user["role"]}
#
# # ── Logs endpoints ────────────────────────────────────────────────
# async def save_log(user_id: str, event: str, score: int):
#     if not db_pool:
#         return
#     try:
#         async with db_pool.acquire() as conn:
#             await conn.execute(
#                 "INSERT INTO session_logs (user_id, event, suspicion_score) VALUES ($1, $2, $3)",
#                 user_id, event, score
#             )
#     except Exception as e:
#         print(f"DB write error: {e}")
#
# @app.get("/logs")
# async def get_logs(current_user=Depends(get_current_user)):
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admin only")
#     async with db_pool.acquire() as conn:
#         rows = await conn.fetch(
#             "SELECT * FROM session_logs ORDER BY timestamp DESC LIMIT 100"
#         )
#     return [dict(r) for r in rows]
#
# @app.get("/my-logs")
# async def get_my_logs(current_user=Depends(get_current_user)):
#     async with db_pool.acquire() as conn:
#         rows = await conn.fetch(
#             "SELECT * FROM session_logs WHERE user_id=$1 ORDER BY timestamp DESC",
#             current_user["username"]
#         )
#     return [dict(r) for r in rows]
#
#
# # ── Question Bank endpoints ───────────────────────────────────────
#
# class QuestionCreate(BaseModel):
#     subject: str
#     question_text: str
#     option_a: str
#     option_b: str
#     option_c: str
#     option_d: str
#     correct_answer: str
#     difficulty: str = "medium"
#
#
# class ExamSubmit(BaseModel):
#     session_id: int
#     answers: dict  # {"question_id": "A/B/C/D"}
#
#
# @app.get("/questions")
# async def get_questions(current_user=Depends(get_current_user)):
#     """Admin gets all questions, student gets random 10"""
#     async with db_pool.acquire() as conn:
#         if current_user["role"] == "admin":
#             rows = await conn.fetch(
#                 "SELECT * FROM questions ORDER BY created_at DESC"
#             )
#         else:
#             rows = await conn.fetch(
#                 "SELECT * FROM questions ORDER BY RANDOM() LIMIT 10"
#             )
#     return [dict(r) for r in rows]
#
#
# @app.post("/questions")
# async def create_question(
#         question: QuestionCreate,
#         current_user=Depends(get_current_user)
# ):
#     """Only admin can create questions"""
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admin only")
#
#     async with db_pool.acquire() as conn:
#         row = await conn.fetchrow(
#             """INSERT INTO questions
#                (subject, question_text, option_a, option_b, option_c, option_d,
#                 correct_answer, difficulty, created_by)
#                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
#                RETURNING *""",
#             question.subject, question.question_text,
#             question.option_a, question.option_b,
#             question.option_c, question.option_d,
#             question.correct_answer.upper(),
#             question.difficulty, current_user["sub"]
#         )
#     return dict(row)
#
#
# @app.put("/questions/{question_id}")
# async def update_question(
#         question_id: int,
#         question: QuestionCreate,
#         current_user=Depends(get_current_user)
# ):
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admin only")
#
#     async with db_pool.acquire() as conn:
#         row = await conn.fetchrow(
#             """UPDATE questions SET
#                subject=$1, question_text=$2,
#                option_a=$3, option_b=$4,
#                option_c=$5, option_d=$6,
#                correct_answer=$7, difficulty=$8
#                WHERE id=$9 RETURNING *""",
#             question.subject, question.question_text,
#             question.option_a, question.option_b,
#             question.option_c, question.option_d,
#             question.correct_answer.upper(),
#             question.difficulty, question_id
#         )
#     if not row:
#         raise HTTPException(status_code=404, detail="Question not found")
#     return dict(row)
#
#
# @app.delete("/questions/{question_id}")
# async def delete_question(
#         question_id: int,
#         current_user=Depends(get_current_user)
# ):
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admin only")
#
#     async with db_pool.acquire() as conn:
#         await conn.execute(
#             "DELETE FROM questions WHERE id=$1", question_id
#         )
#     return {"message": "Question deleted"}
#
#
# @app.post("/exam/start")
# async def start_exam(current_user=Depends(get_current_user)):
#     """Start a new exam session — get random questions"""
#     async with db_pool.acquire() as conn:
#         # Check if student already has active session
#         existing = await conn.fetchrow(
#             """SELECT * FROM exam_sessions
#                WHERE student_id=$1 AND status='active'""",
#             current_user["sub"]
#         )
#         if existing:
#             return dict(existing)
#
#         # Get 10 random questions
#         questions = await conn.fetch(
#             "SELECT id FROM questions ORDER BY RANDOM() LIMIT 10"
#         )
#         question_ids = [q["id"] for q in questions]
#
#         # Create exam session
#         session = await conn.fetchrow(
#             """INSERT INTO exam_sessions
#                (student_id, question_ids, total_questions)
#                VALUES ($1, $2, $3) RETURNING *""",
#             current_user["sub"],
#             question_ids,
#             len(question_ids)
#         )
#     return dict(session)
#
#
# @app.get("/exam/questions/{session_id}")
# async def get_exam_questions(
#         session_id: int,
#         current_user=Depends(get_current_user)
# ):
#     """Get questions for this exam session"""
#     async with db_pool.acquire() as conn:
#         session = await conn.fetchrow(
#             "SELECT * FROM exam_sessions WHERE id=$1 AND student_id=$2",
#             session_id, current_user["sub"]
#         )
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")
#
#         # Get questions WITHOUT correct answers for student
#         questions = await conn.fetch(
#             """SELECT id, subject, question_text,
#                       option_a, option_b, option_c, option_d, difficulty
#                FROM questions WHERE id = ANY($1)""",
#             session["question_ids"]
#         )
#     return {
#         "session": dict(session),
#         "questions": [dict(q) for q in questions]
#     }
#
#
# @app.post("/exam/submit")
# async def submit_exam(
#         data: ExamSubmit,
#         current_user=Depends(get_current_user)
# ):
#     """Submit exam answers and calculate score"""
#     async with db_pool.acquire() as conn:
#         # Get session
#         session = await conn.fetchrow(
#             "SELECT * FROM exam_sessions WHERE id=$1 AND student_id=$2",
#             data.session_id, current_user["sub"]
#         )
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")
#         if session["status"] == "submitted":
#             raise HTTPException(status_code=400, detail="Already submitted")
#
#         # Get correct answers
#         questions = await conn.fetch(
#             "SELECT id, correct_answer FROM questions WHERE id = ANY($1)",
#             session["question_ids"]
#         )
#
#         # Calculate score
#         score = 0
#         for q in questions:
#             student_answer = data.answers.get(str(q["id"]), "")
#             if student_answer.upper() == q["correct_answer"]:
#                 score += 1
#
#         # Update session
#         updated = await conn.fetchrow(
#             """UPDATE exam_sessions SET
#                answers=$1, score=$2, status='submitted',
#                submitted_at=NOW()
#                WHERE id=$3 RETURNING *""",
#             dict(data.answers), score, data.session_id
#         )
#
#     return {
#         "score": score,
#         "total": session["total_questions"],
#         "percentage": round(score / session["total_questions"] * 100),
#         "status": "submitted"
#     }
#
#
# @app.get("/exam/results")
# async def get_all_results(current_user=Depends(get_current_user)):
#     """Admin sees all exam results"""
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admin only")
#
#     async with db_pool.acquire() as conn:
#         rows = await conn.fetch(
#             """SELECT * FROM exam_sessions
#                WHERE status='submitted'
#                ORDER BY submitted_at DESC"""
#         )
#     return [dict(r) for r in rows]
#
#
# @app.get("/exam/my-result")
# async def get_my_result(current_user=Depends(get_current_user)):
#     """Student sees their own result"""
#     async with db_pool.acquire() as conn:
#         row = await conn.fetchrow(
#             """SELECT * FROM exam_sessions
#                WHERE student_id=$1
#                ORDER BY started_at DESC LIMIT 1""",
#             current_user["sub"]
#         )
#     if not row:
#         raise HTTPException(status_code=404, detail="No exam found")
#     return dict(row)
#
# # ── WebSocket ─────────────────────────────────────────────────────
# @app.websocket("/ws/proctor")
# async def proctor_websocket(websocket: WebSocket):
#     await websocket.accept()
#
#     token    = websocket.query_params.get("token", "")
#     username = "anonymous"
#
#     try:
#         payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub", "anonymous")
#     except Exception:
#         pass
#
#     print(f"Client connected: {username}")
#     scorer = SuspicionScorer()
#
#     # try:
#     #     while True:
#     #         raw = await websocket.receive_text()
#     #         if "," in raw:
#     #             raw = raw.split(",")[1]
#     #
#     #         img_bytes = base64.b64decode(raw)
#     #         np_arr    = np.frombuffer(img_bytes, dtype=np.uint8)
#     #         frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#     #
#     #         if frame is None:
#     #             await websocket.send_text(json.dumps({"error": "Bad frame"}))
#     #             continue
#     #
#     #         face_count,            frame = count_faces(frame)
#     #         direction, yaw, pitch, frame = get_head_pose(frame)
#     #         phone_detected,        frame = detect_phone(frame)
#     #         score_data = scorer.update(face_count, direction, phone_detected)
#     #
#     #         for event in score_data["events"]:
#     #             await save_log(username, event, score_data["suspicion_score"])
#     #
#     #         await websocket.send_text(json.dumps({
#     #             "face_count":        face_count,
#     #             "looking_direction": direction,
#     #             "yaw_deg":           yaw,
#     #             "pitch_deg":         pitch,
#     #             "phone_detected":    phone_detected,
#     #             "look_away_secs":    score_data["look_away_secs"],
#     #             "suspicion_score":   score_data["suspicion_score"],
#     #             "events":            score_data["events"],
#     #         }))
#
#     try:
#         while True:
#             raw = await websocket.receive_text()
#
#             # ── Handle tab switch event ──────────────────────────
#             try:
#                 parsed = json.loads(raw)
#                 if isinstance(parsed, dict) and parsed.get("type") == "tab_switch":
#                     await save_log(username, "tab_switch", 40)
#                     await websocket.send_text(json.dumps({"tab_switch_logged": True}))
#                     continue
#             except Exception:
#                 pass
#
#             # ── Handle normal webcam frame ───────────────────────
#             if "," in raw:
#                 raw = raw.split(",")[1]
#
#             img_bytes = base64.b64decode(raw)
#             np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
#             frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#
#             if frame is None:
#                 await websocket.send_text(json.dumps({"error": "Bad frame"}))
#                 continue
#
#             face_count, frame = count_faces(frame)
#             direction, yaw, pitch, frame = get_head_pose(frame)
#             phone_detected, frame = detect_phone(frame)
#             score_data = scorer.update(face_count, direction, phone_detected)
#
#             for event in score_data["events"]:
#                 await save_log(username, event, score_data["suspicion_score"])
#
#             await websocket.send_text(json.dumps({
#                 "face_count": face_count,
#                 "looking_direction": direction,
#                 "yaw_deg": yaw,
#                 "pitch_deg": pitch,
#                 "phone_detected": phone_detected,
#                 "look_away_secs": score_data["look_away_secs"],
#                 "suspicion_score": score_data["suspicion_score"],
#                 "events": score_data["events"],
#             }))
#
#     except WebSocketDisconnect:
#         print(f"Client disconnected: {username}")
#     except Exception as e:
#         print(f"Error: {e}")
#         await websocket.close()
#
#     except WebSocketDisconnect:
#         print(f"Client disconnected: {username}")
#     except Exception as e:
#         print(f"Error: {e}")
#         await websocket.close()



import cv2
import json
import base64
import numpy as np
import sys
import os
import asyncpg
import bcrypt as _bcrypt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt

ML_SERVICE_PATH = os.path.join(os.path.dirname(__file__), "..", "ml-service")
sys.path.append(os.path.abspath(ML_SERVICE_PATH))

from face_detection  import count_faces
from head_pose       import get_head_pose
from phone_detection import detect_phone
from scorer          import SuspicionScorer

# ── Security config ───────────────────────────────────────────────
SECRET_KEY  = "your-secret-key-change-in-production"
ALGORITHM   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ── Database config ───────────────────────────────────────────────


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:shrinetsingh%409648@localhost:5432/proctor_db"
)
# ── Pydantic models ───────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type:   str
    role:         str
    username:     str

class UserCreate(BaseModel):
    username: str
    password: str
    role:     str = "student"

class QuestionCreate(BaseModel):
    subject:        str
    question_text:  str
    option_a:       str
    option_b:       str
    option_c:       str
    option_d:       str
    correct_answer: str
    difficulty:     str = "medium"

class ExamSubmit(BaseModel):
    session_id: int
    answers:    dict

# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(title="AI Proctor — Full System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://ai-proctor.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Database connected successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
        db_pool = None

@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()

# ── Auth helpers ──────────────────────────────────────────────────
def verify_password(plain, hashed):
    return _bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(data: dict):
    to_encode = data.copy()
    expire    = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user(username: str):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE username=$1", username
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return dict(user)

# ── Auth endpoints ────────────────────────────────────────────────
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "username":     user["username"],
    }

@app.post("/register")
async def register(user: UserCreate):
    hashed = _bcrypt.hashpw(user.password.encode(), _bcrypt.gensalt()).decode()
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3)",
                user.username, hashed, user.role
            )
        return {"message": f"User {user.username} created successfully"}
    except Exception:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

# ── Logs endpoints ────────────────────────────────────────────────
async def save_log(user_id: str, event: str, score: int):
    if not db_pool:
        return
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO session_logs (user_id, event, suspicion_score) VALUES ($1, $2, $3)",
                user_id, event, score
            )
    except Exception as e:
        print(f"DB write error: {e}")

@app.get("/logs")
async def get_logs(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM session_logs ORDER BY timestamp DESC LIMIT 100"
        )
    return [dict(r) for r in rows]

@app.get("/my-logs")
async def get_my_logs(current_user=Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM session_logs WHERE user_id=$1 ORDER BY timestamp DESC",
            current_user["username"]
        )
    return [dict(r) for r in rows]

# ── Question Bank endpoints ───────────────────────────────────────
@app.get("/questions")
async def get_questions(current_user=Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        if current_user["role"] == "admin":
            rows = await conn.fetch(
                "SELECT * FROM questions ORDER BY created_at DESC"
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM questions ORDER BY RANDOM() LIMIT 10"
            )
    return [dict(r) for r in rows]

@app.post("/questions")
async def create_question(
    question: QuestionCreate,
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO questions
               (subject, question_text, option_a, option_b, option_c, option_d,
                correct_answer, difficulty, created_by)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
               RETURNING *""",
            question.subject, question.question_text,
            question.option_a, question.option_b,
            question.option_c, question.option_d,
            question.correct_answer.upper(),
            question.difficulty, current_user["username"]
        )
    return dict(row)

@app.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    question: QuestionCreate,
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE questions SET
               subject=$1, question_text=$2,
               option_a=$3, option_b=$4,
               option_c=$5, option_d=$6,
               correct_answer=$7, difficulty=$8
               WHERE id=$9 RETURNING *""",
            question.subject, question.question_text,
            question.option_a, question.option_b,
            question.option_c, question.option_d,
            question.correct_answer.upper(),
            question.difficulty, question_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Question not found")
    return dict(row)

@app.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    async with db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM questions WHERE id=$1", question_id
        )
    return {"message": "Question deleted"}

@app.post("/exam/start")
async def start_exam(current_user=Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT * FROM exam_sessions WHERE student_id=$1 AND status='active'",
            current_user["username"]
        )
        if existing:
            return dict(existing)
        questions = await conn.fetch(
            "SELECT id FROM questions ORDER BY RANDOM() LIMIT 10"
        )
        question_ids = [q["id"] for q in questions]
        session = await conn.fetchrow(
            """INSERT INTO exam_sessions
               (student_id, question_ids, total_questions)
               VALUES ($1, $2, $3) RETURNING *""",
            current_user["username"],
            question_ids,
            len(question_ids)
        )
    return dict(session)

@app.get("/exam/questions/{session_id}")
async def get_exam_questions(
    session_id: int,
    current_user=Depends(get_current_user)
):
    async with db_pool.acquire() as conn:
        session = await conn.fetchrow(
            "SELECT * FROM exam_sessions WHERE id=$1 AND student_id=$2",
            session_id, current_user["username"]
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        questions = await conn.fetch(
            """SELECT id, subject, question_text,
                      option_a, option_b, option_c, option_d, difficulty
               FROM questions WHERE id = ANY($1)""",
            session["question_ids"]
        )
    return {
        "session": dict(session),
        "questions": [dict(q) for q in questions]
    }

@app.post("/exam/submit")
async def submit_exam(
    data: ExamSubmit,
    current_user=Depends(get_current_user)
):
    async with db_pool.acquire() as conn:
        session = await conn.fetchrow(
            "SELECT * FROM exam_sessions WHERE id=$1 AND student_id=$2",
            data.session_id, current_user["username"]
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session["status"] == "submitted":
            raise HTTPException(status_code=400, detail="Already submitted")
        questions = await conn.fetch(
            "SELECT id, correct_answer FROM questions WHERE id = ANY($1)",
            session["question_ids"]
        )
        score = 0
        for q in questions:
            student_answer = data.answers.get(str(q["id"]), "")
            if student_answer.upper() == q["correct_answer"]:
                score += 1
        updated = await conn.fetchrow(
            """UPDATE exam_sessions SET
               answers=$1, score=$2, status='submitted',
               submitted_at=NOW()
               WHERE id=$3 RETURNING *""",
            dict(data.answers), score, data.session_id
        )
    return {
        "score":      score,
        "total":      session["total_questions"],
        "percentage": round(score / session["total_questions"] * 100),
        "status":     "submitted"
    }

@app.get("/exam/results")
async def get_all_results(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM exam_sessions WHERE status='submitted' ORDER BY submitted_at DESC"
        )
    return [dict(r) for r in rows]

@app.get("/exam/my-result")
async def get_my_result(current_user=Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM exam_sessions WHERE student_id=$1 ORDER BY started_at DESC LIMIT 1",
            current_user["username"]
        )
    if not row:
        raise HTTPException(status_code=404, detail="No exam found")
    return dict(row)

# ── WebSocket ─────────────────────────────────────────────────────
@app.websocket("/ws/proctor")
async def proctor_websocket(websocket: WebSocket):
    await websocket.accept()

    token    = websocket.query_params.get("token", "")
    username = "anonymous"

    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub", "anonymous")
    except Exception:
        pass

    print(f"Client connected: {username}")
    scorer = SuspicionScorer()

    try:
        while True:
            raw = await websocket.receive_text()

            # Handle tab switch event
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict) and parsed.get("type") == "tab_switch":
                    await save_log(username, "tab_switch", 40)
                    await websocket.send_text(json.dumps({"tab_switch_logged": True}))
                    continue
            except Exception:
                pass

            # Handle webcam frame
            if "," in raw:
                raw = raw.split(",")[1]

            img_bytes = base64.b64decode(raw)
            np_arr    = np.frombuffer(img_bytes, dtype=np.uint8)
            frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                await websocket.send_text(json.dumps({"error": "Bad frame"}))
                continue

            face_count,            frame = count_faces(frame)
            direction, yaw, pitch, frame = get_head_pose(frame)
            phone_detected,        frame = detect_phone(frame)
            score_data = scorer.update(face_count, direction, phone_detected)

            for event in score_data["events"]:
                await save_log(username, event, score_data["suspicion_score"])

            await websocket.send_text(json.dumps({
                "face_count":        face_count,
                "looking_direction": direction,
                "yaw_deg":           yaw,
                "pitch_deg":         pitch,
                "phone_detected":    phone_detected,
                "look_away_secs":    score_data["look_away_secs"],
                "suspicion_score":   score_data["suspicion_score"],
                "events":            score_data["events"],
            }))

    except WebSocketDisconnect:
        print(f"Client disconnected: {username}")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

