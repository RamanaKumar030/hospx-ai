from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

# ---------------- LLM ----------------
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=500
)

# ---------------- AGENT ----------------
agent = Agent(
    role="Medical Triage AI",
    goal="Return strict JSON medical triage output",
    backstory="You are a hospital emergency triage AI that outputs only structured JSON.",
    llm=llm,
    verbose=False
)

# ---------------- TASK (IMPORTANT FIXED BRACES) ----------------
task = Task(
    description="""
You are a medical triage AI.

Analyze symptoms:
{symptoms}

RULES:
- Output ONLY valid JSON
- No markdown
- No explanations
- No extra text

Return EXACT format:

{{
  "severity": "Low | Medium | High | Critical",
  "urgency": "Non-urgent | Urgent | Emergency",
  "possible_conditions": ["condition1", "condition2", "condition3"],
  "recommended_department": "string"
}}
""",
    expected_output="Strict JSON output only",
    agent=agent
)

# ---------------- CREW ----------------
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=False
)

# ---------------- SAFE JSON PARSER ----------------
def extract_json(text: str):
    try:
        # clean markdown if any
        cleaned = text.replace("```json", "").replace("```", "").strip()

        # find JSON block
        match = re.search(r"\{[\s\S]*\}", cleaned)

        if match:
            return json.loads(match.group())

    except Exception:
        return None

    return None

# ---------------- MAIN FUNCTION ----------------
def run_crew(symptoms: str):
    try:
        symptoms = symptoms[:300]

        result = crew.kickoff(inputs={"symptoms": symptoms})

        raw = str(result)

        parsed = extract_json(raw)

        if parsed and isinstance(parsed, dict):
            return parsed

        # ---------------- FALLBACK (NEVER FAIL API) ----------------
        return {
            "severity": "High",
            "urgency": "Emergency",
            "possible_conditions": [
                "Cardiac Issue",
                "Respiratory Distress",
                "Unknown Condition"
            ],
            "recommended_department": "Emergency Medicine"
        }

    except Exception as e:
        return {
            "severity": "Critical",
            "urgency": "Emergency",
            "possible_conditions": ["System Error"],
            "recommended_department": "Emergency Medicine",
            "error": str(e)
        }