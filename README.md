# ArogyaMitra ✦ Your AI Fitness Companion

ArogyaMitra (Healthy Friend) is a production-ready AI-powered fitness platform featuring **AROMI**, your personalized Indian health coach. It generates custom workout and nutrition plans, tracks your progress, and turns your fitness achievements into charitable donations.

## ✨ Key Features
- **🤖 AROMI AI Coach**: Personalized guidance using LLaMA-3.3-70b (via Groq).
- **🏋️ Dynamic Workouts**: 7-day personalized plans with YouTube tutorials & smart timer.
- **🥗 Indian Nutrition**: Traditional & modern Indian meal plans geared for your goals.
- **📈 Progress Tracking**: Visual analytics of your weight, calories, and consistency.
- **❤️ Health-to-Charity**: Every workout and meal logged contributes to health charities.
- **📅 Smart Sync**: Automatic Google Calendar integration (setup required).
- **🌓 Modern UI**: Premium glassmorphism dark theme with responsive design.

## 🚀 Quick Start

### 1. Prerequisites
- Node.js (v18+)
- Python (3.9+)
- [Groq API Key](https://console.groq.com/)
- [YouTube Data API Key](https://console.cloud.google.com/apis/library/youtube.googleapis.com)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend/` directory:
```env
SECRET_KEY=generate_a_secure_random_string
GROQ_API_KEY=your_groq_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Running the App
**Start Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```
**Start Frontend:**
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🛠 Tech Stack
- **Frontend**: React, Vite, Tailwind CSS, Framer Motion, Zustand, Recharts, Axios.
- **Backend**: FastAPI, SQLAlchemy, SQLite, Pydantic, python-jose.
- **AI/APIs**: Groq (LLaMA-3.3), YouTube Data API v3, BigBasket links.

## 🤝 Contribution
Contribution welcome! Join us in making the world healthier.
