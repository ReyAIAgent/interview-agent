import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

from agent_interviewer import generate_personalized_question

# New version supports history input
def generate_interview_question(resume_text: str, job_description: str, qa_history: list = None) -> str:
    return generate_personalized_question(resume_text, job_description, history=qa_history)
