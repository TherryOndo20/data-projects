import anthropic
import json
import os
import streamlit as st

api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

SYSTEM_PROMPT = """You are an expert IT support triage agent for an enterprise software company.

Your job is to analyze incoming IT support tickets and return a structured JSON response.

For each ticket, you must return ONLY a valid JSON object with this exact structure:
{
  "category": "<one of: Network, Security, Access & Permissions, Hardware, Software, Email & Communication, Data & Backup, Other>",
  "priority": "<one of: Critical, High, Medium, Low>",
  "priority_reason": "<one sentence explaining the priority level>",
  "summary": "<2-3 sentence structured summary of the issue for the technician>",
  "suggested_reply": "<professional first response to send to the user, in the same language as the ticket>",
  "estimated_resolution_time": "<e.g. 15 minutes, 2 hours, 1 day>",
  "tags": ["<tag1>", "<tag2>", "<tag3>"]
}

Priority guidelines:
- Critical: System down, security breach, data loss, blocking entire team
- High: Major functionality broken, blocking one person's work
- Medium: Partial functionality issue, workaround exists
- Low: Minor inconvenience, cosmetic issue, general question

Return ONLY the JSON object, no explanation, no markdown, no preamble.
"""

def triage_ticket(ticket_text: str, user_name: str = "", department: str = "") -> dict:
    """
    Send a ticket to Claude for triage and return structured results.
    """
    context = ""
    if user_name:
        context += f"Submitted by: {user_name}\n"
    if department:
        context += f"Department: {department}\n"
    if context:
        context += "\n"

    user_message = f"{context}Ticket:\n{ticket_text}"

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    response_text = message.content[0].text.strip()

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        result = {
            "category": "Other",
            "priority": "Medium",
            "priority_reason": "Could not parse response automatically.",
            "summary": response_text,
            "suggested_reply": "Thank you for contacting IT support. We have received your ticket and will get back to you shortly.",
            "estimated_resolution_time": "Unknown",
            "tags": []
        }

    return result


PRIORITY_COLORS = {
    "Critical": "#FF3B3B",
    "High": "#FF8C00",
    "Medium": "#FFD700",
    "Low": "#4CAF50"
}

CATEGORY_ICONS = {
    "Network": "🌐",
    "Security": "🔒",
    "Access & Permissions": "🔑",
    "Hardware": "🖥️",
    "Software": "⚙️",
    "Email & Communication": "📧",
    "Data & Backup": "💾",
    "Other": "📋"
}
