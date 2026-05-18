from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=500
)

agent = Agent(
    role="Medical Triage AI",
    goal="Return strict JSON medical triage output",
    backstory="You are a hospital emergency triage AI that outputs only structured JSON.",
    llm=llm,
    verbose=False
)

task = Task(
    description="""
Analyze symptoms:
{symptoms}

Return ONLY valid JSON.

{{
  "severity": "Low | Medium | High | Critical",
  "urgency": "Non-urgent | Urgent | Emergency",
  "possible_conditions": ["condition1", "condition2", "condition3"],
  "recommended_department": "string"
}}
""",
    expected_output="Strict JSON only",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=False
)

def extract_json(text: str):
    try:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group())
    except:
        return None
    return None


def rule_based_fallback(symptoms: str):
    s = symptoms.lower()

    emergency_words = [
        "chest pain", "shortness of breath", "unconscious",
        "no pulse", "weak pulse", "severe bleeding",
        "stroke", "blue lips", "not breathing"
    ]

    high_words = [
        "severe headache", "vomiting blood", "high fever",
        "confusion", "fainting", "seizure"
    ]

    if any(w in s for w in emergency_words):
        return {
            "severity": "Critical",
            "urgency": "Emergency",
            "possible_conditions": [
                "Cardiac Emergency",
                "Respiratory Distress",
                "Neurological Emergency"
            ],
            "recommended_department": "Emergency Medicine"
        }

    if any(w in s for w in high_words):
        return {
            "severity": "High",
            "urgency": "Urgent",
            "possible_conditions": [
                "Serious Medical Condition",
                "Neurological Issue",
                "Infection"
            ],
            "recommended_department": "Emergency Medicine"
        }

    return {
        "severity": "Low",
        "urgency": "Non-urgent",
        "possible_conditions": [
            "Tension Headache",
            "Fatigue",
            "Minor Illness"
        ],
        "recommended_department": "General Medicine"
    }


def run_crew(symptoms: str):
    symptoms = symptoms[:300]

    try:
        result = crew.kickoff(inputs={"symptoms": symptoms})
        raw = str(result)
        parsed = extract_json(raw)

        if parsed and isinstance(parsed, dict):
            return parsed

        return rule_based_fallback(symptoms)

    except Exception:
        return rule_based_fallback(symptoms)