# 🛡️ AI-Powered Online Exam Proctoring System

> A full-stack real-time exam proctoring system that uses computer vision and AI to detect cheating behaviors during online exams.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=flat-square)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-00C851?style=flat-square)

---

## ✨ Features

- 🎯 **Real-time face detection** — flags if more than one person is visible
- 👀 **Gaze tracking** — detects if student is looking away from screen
- 📱 **Phone detection** — uses YOLOv8 to detect mobile phones in frame
- 🔐 **JWT Authentication** — student and admin login with role-based access
- 📊 **Admin Dashboard** — live session logs with suspicion scores
- 💾 **PostgreSQL logging** — every suspicious event saved with timestamp
- ⚡ **WebSocket streaming** — real-time low-latency communication
- 🚨 **Suspicion scoring** — additive scoring combining all detection signals

---

## 🧠 How It Works
```
Student webcam (browser)
        ↓  WebSocket (base64 frames every 500ms)
FastAPI backend
        ↓  Runs 3 AI detectors
   ├── MediaPipe Face Detection  → face count
   ├── MediaPipe Face Mesh + OpenCV solvePnP  → gaze direction
   └── YOLOv8  → phone detection
        ↓
Suspicion Scorer → PostgreSQL (saves events)
        ↓
React frontend (updates HUD live)
```

---

## 📊 Suspicion Scoring System

| Event | Points | Trigger |
|---|---|---|
| Phone visible | +50 | Instant |
| Multiple faces | +40 | Instant |
| No face | +30 | Instant |
| Looking away | +20 | After 3 continuous seconds |
| **Maximum** | **100** | Capped |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Face Detection | MediaPipe |
| Gaze Tracking | OpenCV + solvePnP |
| Phone Detection | YOLOv8 (Ultralytics) |
| Backend | FastAPI + WebSocket |
| Authentication | JWT (python-jose) + bcrypt |
| Database | PostgreSQL 16 + asyncpg |
| Frontend | React 18 |

---

## 📁 Project Structure
```
ai-proctor/
├── ml-service/
│   ├── main.py              # Standalone webcam testing
│   ├── face_detection.py    # MediaPipe face counter
│   ├── head_pose.py         # Gaze direction via solvePnP
│   ├── phone_detection.py   # YOLOv8 phone detector
│   └── scorer.py            # Suspicion scoring logic
│
├── backend/
│   └── server.py            # FastAPI + WebSocket + Auth + DB
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Camera.jsx
│       │   ├── DetectionHUD.jsx
│       │   ├── ExamPanel.jsx
│       │   ├── AdminDashboard.jsx
│       │   └── LoginPage.jsx
│       ├── hooks/
│       │   └── useProctor.js
│       └── App.jsx
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10
- Node.js 18+
- PostgreSQL 16
- Webcam

### 1. Clone the repository
```bash
git clone https://github.com/Shrinetsingh9648/ai-proctor.git
cd ai-proctor
```

### 2. Set up database
```bash
psql -U postgres
```
```sql
CREATE DATABASE proctor_db;
\c proctor_db
CREATE TABLE session_logs (id SERIAL PRIMARY KEY, user_id VARCHAR(50), event VARCHAR(100), suspicion_score INTEGER, timestamp TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL, role VARCHAR(10) NOT NULL DEFAULT 'student');
\q
```

### 3. Set up backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn websockets asyncpg bcrypt==4.0.1 python-jose[cryptography] python-multipart opencv-python mediapipe numpy ultralytics
```

Update password in `backend/server.py`:
```python
DB_CONFIG = {
    "password": "YOUR_POSTGRES_PASSWORD",
}
```

Start backend:
```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Register users
```bash
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\",\"role\":\"admin\"}"
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d "{\"username\":\"student1\",\"password\":\"admin123\",\"role\":\"student\"}"
```

### 5. Set up frontend
```bash
cd frontend
npm install
npm start
```

Browser opens at `http://localhost:3000`

---

## 🔑 Demo Accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Admin Dashboard |
| `student1` | `admin123` | Exam View |

---

## 🗺️ Roadmap

- [x] Face detection
- [x] Gaze tracking
- [x] Phone detection
- [x] JWT Authentication
- [x] PostgreSQL logging
- [x] Admin dashboard
- [ ] Tab switching detection
- [ ] Noise detection
- [ ] Auto PDF report generation
- [ ] Cloud deployment

---

## 👨‍💻 Author

**Shrinet Singh**
Built as a portfolio project demonstrating full-stack AI engineering.

🔗 GitHub: [Shrinetsingh9648](https://github.com/Shrinetsingh9648)

---

## 📄 License

MIT License — free to use and modify.