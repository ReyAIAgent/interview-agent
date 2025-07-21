import spacy
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# Load OpenAI model
llm = ChatOpenAI(model="gpt-4", temperature=0.2)

# Prompt for OpenAI
from langchain.prompts import ChatPromptTemplate

openai_prompt = ChatPromptTemplate.from_template("""
You are an expert resume analyzer.

Given the following resume text, extract the following:
- **Hard Skills**: Technical skills such as programming languages, tools, frameworks, and domain expertise (e.g., Python, SQL, Machine Learning, TensorFlow, etc.).
- **Soft Skills**: Personal and interpersonal attributes like communication, adaptability, teamwork, etc.
- **Experience Summary**: A 2–4 sentence high-level overview of the candidate's professional background, domains worked in, and key contributions.
- **Behavioral Traits**: Insights into personality, work ethic, or leadership style inferred from the resume.

Respond **only** in this exact JSON format (inside triple backticks):

```json
{{
  "hard_skills": "<comma-separated list of technical skills>",
  "soft_skills": "<comma-separated list of interpersonal skills>",
  "experience_summary": "<2-4 sentence summary>",
  "behavioral_traits": "<1-2 sentence behavioral insight>"
}}
Resume:
{resume_text}
""")


openai_chain = openai_prompt | llm

def extract_hard_skills_with_spacy(text):
    """Extract potential skills using noun chunks and known tech keywords."""
    doc = nlp(text)
    keywords = {"python", "machine learning", "data analysis", "pytorch", "tensorflow", "nlp", "sql", "aws", "linux", "deep learning", "graph neural networks", "network science"}
    found = set()

    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        for kw in keywords:
            if kw in chunk_text:
                found.add(kw.title())

    return list(sorted(found))



import json
import re

def extract_resume_insights(resume_text: str) -> dict:
    """Use LLM to extract all resume insights, including skills."""
    try:
        print("=== RESUME TEXT ===")
        print(resume_text[:4000])

        llm_result = openai_chain.invoke({"resume_text": resume_text})
        content = llm_result.content if hasattr(llm_result, "content") else str(llm_result)

        print("=== LLM RAW OUTPUT ===")
        print(content)

        # Extract JSON from triple backticks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(1))
        else:
            print("No valid JSON found in LLM output.")
            parsed = {}

    except Exception as e:
        print("LLM error:", e)
        parsed = {}

    # Use soft_skills for UI "Skills" if "skills" key is missing or empty
    skills_fallback = parsed.get("skills") or parsed.get("soft_skills", "N/A")

    return {
    "hard_skills": parsed.get("hard_skills", "N/A"),
    "soft_skills": parsed.get("soft_skills", "N/A"),
    "experience_summary": parsed.get("experience_summary", "N/A"),
    "behavioral_traits": parsed.get("behavioral_traits", "N/A")
}


