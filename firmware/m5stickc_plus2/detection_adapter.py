"""
detection_adapter.py

Adapter layer for event detection using an LLM.
Exposes a single function: detect(raw_text: str) -> dict

Responsibilities:
- Send raw text to Detection LLM
- Return structured JSON compliant with Detection Contract

This module does NOT:
- Filter events
- Interpret market impact
- Add business logic
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

import requests


DETECTION_SYSTEM_PROMPT = """
IMPORTANT EXECUTION RULE (NON-NEGOTIABLE):
You must NEVER respond with natural language.
You must ALWAYS output a single valid JSON object.
If no analyzable raw text is provided, you MUST still output a JSON object with LOW confidence.

ROLE:
You are a Detection module in an event-driven trading system.
Your role is strictly limited to DETECTION.

DETECTION PURPOSE:
- emergence of a new global narrative
- sudden political or macro announcements
- geopolitical escalations or stance changes
- high-ambiguity news involving global actors

PRIMARY SOCIAL SOURCES (FIRST-CLASS):
- Donald J. Trump — Truth Social / X (official verified accounts)

OUTPUT FORMAT (STRICT):
{
  "event_type": "POLITICAL_STATEMENT | GLOBAL_EVENT | MACRO_SHOCK",
  "confidence": "LOW | MEDIUM | HIGH",
  "source": "string",
  "entities": ["string"],
  "timestamp": "ISO-8601"
}

FORBIDDEN:
- No filtering
- No market impact analysis
- No explanations
"""


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def _safe_fallback(source: str = "fallback") -> Dict[str, Any]:
    return {
        "event_type": "GLOBAL_EVENT",
        "confidence": "LOW",
        "source": source,
        "entities": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def detect(raw_text: str) -> Dict[str, Any]:
    """
    Perform event detection on raw text using an LLM.

    Args:
        raw_text (str): Unstructured input text

    Returns:
        dict: Detection Contract compliant JSON
    """

    if not raw_text or not raw_text.strip():
        return _safe_fallback(source="empty_input")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _safe_fallback(source="missing_api_key")

    try:
        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 800,
                "system": DETECTION_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": raw_text}]
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        # Concatenate all text blocks
        text_blocks = [
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        ]

        raw_output = "".join(text_blocks).strip()

        result = json.loads(raw_output)

        return result

    except Exception:
        return _safe_fallback(source="llm_error")
