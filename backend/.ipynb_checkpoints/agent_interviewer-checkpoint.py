from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Initialize the model
llm = ChatOpenAI(temperature=0.3, model="gpt-4")

# prompt with adaptive logic
prompt_template = ChatPromptTemplate.from_template("""
You are an AI technical interviewer.

Given the candidate's resume and the job description, ask a personalized, role-specific, technical interview question.

Use the following context:
- If there is prior Q&A history, consider the candidate’s weaknesses or unanswered aspects and tailor your next question accordingly.
- If previous scores were high (e.g., 4-5), increase difficulty slightly.
- If a topic appears repeatedly with low scores (<= 2), ask follow-up questions on that topic.

Resume:
{resume_text}

Job Description:
{job_description}

Previous Q&A History:
{history}

Weak Topics:
{weak_topics}

Should Increase Difficulty:
{increase_difficulty}

Your next question:
""")

# Define the LLMChain using the updated prompt
chain = LLMChain(llm=llm, prompt=prompt_template)

# This function will be called from question_generator.py
def generate_personalized_question(resume_text: str, job_description: str, history=None) -> str:
    history_str = ""
    weak_topics = set()
    increase_difficulty = False

    if history:
        for i, qa in enumerate(history[-3:]):  # include last 3 entries
            history_str += f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}\n"
            if qa.get("score", 3) <= 2 and qa.get("topic"):
                weak_topics.add(qa["topic"])
        if all(qa.get("score", 0) >= 4 for qa in history[-2:]):
            increase_difficulty = True

    response = chain.run({
        "resume_text": resume_text,
        "job_description": job_description,
        "history": history_str or "None",
        "weak_topics": ", ".join(weak_topics) or "None",
        "increase_difficulty": "Yes" if increase_difficulty else "No"
    })
    return response.strip()

