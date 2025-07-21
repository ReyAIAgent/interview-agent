from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser  


llm = ChatOpenAI(temperature=0.5, model="gpt-4")

from langchain_openai import ChatOpenAI

def generate_coaching_tip(rubric: dict) -> str:
    tips = []
    if rubric.get("relevance", 3) <= 2:
        tips.append("Try to address the question more directly.")
    if rubric.get("technical_accuracy", 3) <= 2:
        tips.append("Include more technical details and specific terminology.")
    if rubric.get("clarity", 3) <= 2:
        tips.append("Make your response clearer and more structured.")
    if rubric.get("job_alignment", 3) <= 2:
        tips.append("Connect your answer more clearly to the job responsibilities.")
    
    if tips:
        return "Coaching Tips:\n- " + "\n- ".join(tips)
    else:
        return "Great job! Your response meets expectations across the board."


def generate_coaching_tip_ai(rubric: dict, feedback: str, answer: str) -> str:
    coaching_prompt = ChatPromptTemplate.from_template("""
You are a career coach helping candidates improve their technical interview answers.

Given the evaluation rubric, summary feedback, and optionally the candidate’s answer, provide 2–4 concise and actionable coaching tips.

Format them as a bulleted list, for example:

- Improve clarity by structuring your response.
- Add more specific technical terminology.

Rubric:
{rubric}

Feedback:
{feedback}

Candidate Answer:
{answer}

Coaching Tips:
""")

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    prompt = coaching_prompt.format_messages(
        rubric=rubric,
        feedback=feedback,
        answer=answer
    )
    result = llm.invoke(prompt)
    return result.content.strip()

def evaluate_answer_with_chain(resume_text, job_description, question, answer):
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt = ChatPromptTemplate.from_template("""
You are an AI interview evaluator. Based on the candidate's resume, job description, and their answer to the interview question, grade their response using the following rubric:

Rubric (1-5 for each):
- Relevance: How directly the answer addresses the question.
- Technical Accuracy: How technically sound and specific the answer is.
- Clarity: How clearly the answer is communicated.
- Job Alignment: How well the answer aligns with the responsibilities and requirements of the job description.

Output your answer in the following JSON format:

{{
    "relevance": <1-5>,
    "technical_accuracy": <1-5>,
    "clarity": <1-5>,
    "job_alignment": <1-5>,
    "overall_score": <average of above>,
    "feedback": "<1-2 sentence justification>"
}}

Resume:
{resume}

Job Description:
{jd}

Interview Question:
{question}

Candidate Answer:
{answer}
""")

    chain = prompt | llm | JsonOutputParser()

    result = chain.invoke({
        "resume": resume_text,
        "jd": job_description,
        "question": question,
        "answer": answer
    })
    #  Add coaching tips
    
    coaching = generate_coaching_tip_ai(
    rubric=result,
    feedback=result["feedback"],
    answer=answer
    )
    result["coaching"] = coaching

    return result


def extract_score(text):
    import re
    match = re.search(r"(\bscore\b|\brating\b)[^\d]*(\d{1,2})", text, re.IGNORECASE)
    if match:
        return int(match.group(2))
    return None

def extract_feedback(text):
    lines = text.strip().splitlines()
    return "\n".join([line for line in lines if not line.strip().lower().startswith("score")])
