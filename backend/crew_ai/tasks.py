from crewai import Task

from .agents import (
    triage_agent,
    emergency_agent,
    routing_agent,
    risk_agent,
    report_agent
)

def get_tasks(symptoms):

    triage_task = Task(
        description=f"""
        Analyze the following patient symptoms:

        {symptoms}

        Determine:
        - severity level
        - urgency
        - possible medical concerns

        Categorize:
        - Low
        - Medium
        - High
        - Critical
        """,
        expected_output="Patient triage assessment",
        agent=triage_agent
    )

    emergency_task = Task(
        description=f"""
        Analyze these symptoms for emergency indicators:

        {symptoms}

        Detect:
        - stroke symptoms
        - cardiac emergency
        - breathing distress
        - internal bleeding
        - neurological emergencies

        Decide whether emergency escalation is required.
        """,
        expected_output="Emergency detection analysis",
        agent=emergency_agent
    )

    routing_task = Task(
        description=f"""
        Determine which hospital department should
        handle this patient:

        Symptoms:
        {symptoms}

        Examples:
        - Cardiology
        - Neurology
        - Orthopedics
        - Emergency
        - Pulmonology
        - General Medicine
        """,
        expected_output="Hospital department recommendation",
        agent=routing_agent
    )

    risk_task = Task(
        description=f"""
        Predict patient risk level:

        Symptoms:
        {symptoms}

        Estimate:
        - hospitalization probability
        - ICU probability
        - severity progression risk
        """,
        expected_output="Medical risk prediction",
        agent=risk_agent
    )

    report_task = Task(
        description="""
        Generate a final structured hospital intelligence report.

        Include:
        - triage summary
        - emergency findings
        - hospital department
        - hospitalization risk
        - precautions
        - next steps

        Add disclaimer:
        'This system does not provide professional medical advice.'
        """,
        expected_output="Professional hospital report",
        agent=report_agent
    )

    return [
        triage_task,
        emergency_task,
        routing_task,
        risk_task,
        report_task
    ]