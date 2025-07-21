from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
#from resume_parser import extract_text_from_pdf
from models import ResumeUpload, JobDescriptionUpload, InterviewInput, EvaluationInput, AnswerInput
from question_generator import generate_personalized_question as generate_interview_question
from evaluator import evaluate_answer_with_chain
from loaders import parse_document
from resume_analysis import extract_resume_insights
import openai
import shutil
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
#from pydub import AudioSegment


class TTSRequest(BaseModel):
    text: str

# In-memory interview session storage
interview_session = {
    "resume_text": "",
    "job_description": "",
    "qa_history": [],
    "current_question": ""
}


app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload Resume
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    contents = await file.read()
    with open("resume.pdf", "wb") as f:
        f.write(contents)

    parsed_text = parse_document("resume.pdf")
    interview_session["resume_text"] = parsed_text
    return {"message": "Resume uploaded and parsed."}

@app.get("/resume/insights")
async def analyze_resume():
    resume = interview_session.get("resume_text", "")
    if not resume:
        return {"error": "No resume has been uploaded yet."}
    
    result = extract_resume_insights(resume)
    return result


# Upload Job Description
@app.post("/upload-jd/")
async def upload_job_description(file: UploadFile = File(...)):
    # 1. Save file to disk
    with open("job_description.txt", "wb") as f:
        f.write(await file.read())

    job_text = parse_document("job_description.txt")
    interview_session["job_description"] = job_text
    return {"job_text": job_text}



    
# Start Interview Session
@app.get("/interview/start")
async def start_interview():
    interview_session["qa_history"] = []
    interview_session["current_question"] = ""
    return {"message": "Interview session started. Now upload resume and job description."}

# Generate Next Question
@app.get("/interview/next")
async def next_question():
    resume = interview_session["resume_text"]
    jd = interview_session["job_description"]
    qa_history = interview_session.get("qa_history", [])

    if not resume or not jd:
        return {"error": "Missing resume or job description."}

    question = generate_interview_question(resume, jd, qa_history)
    interview_session["current_question"] = question
    return {"question": question}

# Submit Answer and Get Feedback
@app.post("/interview/answer")
async def answer_question(data: AnswerInput):
    resume = interview_session["resume_text"]
    jd = interview_session["job_description"]
    question = interview_session["current_question"]

    if not question:
        return {"error": "No question has been asked yet. Please call /interview/next first."}

    result = evaluate_answer_with_chain(
        resume_text=resume,
        job_description=jd,
        question=question,
        answer=data.answer
    )
    

    
    interview_session["qa_history"].append({
    "question": question,
    "answer": data.answer,
    "score": result.get("score", result.get("overall_score")),
    "feedback": result["feedback"],
    "coaching": result.get("coaching", "")
})


    interview_session["current_question"] = ""
    return {
    "score": result.get("overall_score") or result.get("overall_score"),
    "rubric": {
        "relevance": result.get("relevance"),
        "technical_accuracy": result.get("technical_accuracy"),
        "clarity": result.get("clarity"),
        "job_alignment": result.get("job_alignment")
    },
    "feedback": result.get("feedback", "No feedback provided."),
    "coaching": result.get("coaching", "")
}

   


# View Full Interview History
@app.get("/interview/history/")
async def get_interview_history():
    return {"history": interview_session["qa_history"]}


# ===  Voice AI Endpoints ===
from openai import OpenAI
client = OpenAI()

import subprocess

@app.post("/interview/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    input_path = "input.webm"
    output_path = "converted.wav"

    print("==> Starting transcription")

    try:
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("✅ Saved audio to", input_path)

        # Run FFmpeg with full path (recommended)
        ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"  # Update if different
        result = subprocess.run([
        ffmpeg_path, "-y", "-f", "webm", "-i", input_path,
        "-ar", "16000", "-ac", "1", output_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=4096  #  use an integer!
        )




        if result.returncode != 0:
            return {"error": f"FFmpeg failed: {result.stderr}"}

        if not os.path.exists(output_path):
            return {"error": "FFmpeg did not produce 'converted.wav'"}

        # Transcribe using OpenAI Whisper
        with open(output_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            print(" Transcription complete")
            return {"transcript": transcript.text}

    except Exception as e:
        print(" Exception occurred:", e)
        return {"error": f"Unexpected error: {str(e)}"}

    finally:
        print("Cleaning up")
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)


@app.post("/tts")
async def text_to_speech(data: TTSRequest):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=data.text
    )
    with open("response.mp3", "wb") as f:
        f.write(response.content)

    return FileResponse(
        path="response.mp3",
        media_type="audio/mpeg",
        filename="response.mp3"
    )

