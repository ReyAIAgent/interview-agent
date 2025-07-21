# AI Interview Agent

A full-stack AI-powered interview simulation system that provides personalized questions, captures spoken answers, and delivers rubric-based feedback and coaching — all tailored to your resume and job description.

---

##  Features

-  **Role-Specific Question Generation**
-  **Voice Answering & Transcription**
-  **Resume and Job Description Analysis**
-  **Rubric-Based Evaluation**
-  **Real-Time Coaching Tips**
-  **Text-to-Speech Support**

---

##  Project Structure
.
├── backend/
│ ├── agent_interviewer.py
│ ├── evaluator.py
│ ├── loaders.py
│ ├── main.py
│ ├── models.py
│ ├── question_generator.py
│ ├── resume_analysis.py
│ └── requirements.txt
├── frontend/
│ ├── public/
│ ├── src/
│ │ └── App.js
│ ├── .gitignore
│ └── package.json
└── README.md

---

##  Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install requirements:
   pip install -r requirements.txt
4. Start the API server:
   uvicorn main:app --reload

##  Frontend Setup (React)
1. Navigate to the frontend directory:
   cd frontend
2. Install dependencies:
   npm install
3. Start the React development server:
   npm start

##  Notes
Make sure ffmpeg is installed and added to your system PATH.
Audio recordings are saved and transcribed using Whisper or pydub.
