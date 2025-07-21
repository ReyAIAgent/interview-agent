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

    #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