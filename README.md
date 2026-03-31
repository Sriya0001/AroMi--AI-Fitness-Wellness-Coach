# 🧠 AroMi – AI Fitness & Wellness Coach

An AI-powered fitness and wellness platform that generates **personalized workout and nutrition plans** based on user data, goals, and progress.

---

## 🚀 Features

- 🤖 AI-powered adaptive coaching using LLaMA (Groq)
- 🏋️ Personalized workout plans based on fitness level & goals
- 🥗 Smart nutrition planning with Spoonacular API integration
- 📅 Calendar-based scheduling for workouts and meals
- 📊 Progress tracking with dynamic dashboards
- 🔐 Secure authentication using JWT
- 🎧 Spotify integration for workout playlists
- 🎥 YouTube integration for guided exercises

---

## 🛠️ Tech Stack

### Backend
- FastAPI
- SQLite
- JWT Authentication
- LangChain + LLaMA (Groq)
- REST APIs

### Frontend
- React.js
- Tailwind CSS
- Zustand
- Vite

---

## ⚙️ Setup Instructions

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload