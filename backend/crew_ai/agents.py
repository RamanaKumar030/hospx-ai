from crewai import Agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=400
)

medical_agent = Agent(
    role="Hospital Triage AI",
    goal="Return structured medical triage JSON",
    backstory="""
You are a hospital emergency triage system.

You NEVER:
- explain reasoning
- use markdown
- use natural language
- call tools
- delegate tasks

You ONLY output valid JSON.
""",
    llm=llm,
    verbose=False,
    allow_delegation=False
)