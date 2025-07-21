from pydantic import BaseModel

class ResumeUpload(BaseModel):
    resume_text: str

class JobDescriptionUpload(BaseModel):
    job_text: str

class InterviewInput(BaseModel):
    resume_text: str
    job_description: str
    previous_answers: str = ""
class EvaluationInput(BaseModel):
    resume_text: str
    job_description: str
    question: str
    answer: str

class AnswerInput(BaseModel):
    answer: str

   
