import re

DANGEROUS_KEYWORDS = [
    "suicide", "kill", "self-harm", "overdose",
    "poison", "die", "fatal"
]

def safety_filter(symptoms: str):
    text = symptoms.lower()

    for word in DANGEROUS_KEYWORDS:
        if word in text:
            return {
                "safe": False,
                "message": "Emergency mental health protocol triggered. Seek immediate professional help."
            }

    # remove garbage input
    if len(symptoms.strip()) < 5:
        return {
            "safe": False,
            "message": "Invalid symptom input"
        }

    return {"safe": True}