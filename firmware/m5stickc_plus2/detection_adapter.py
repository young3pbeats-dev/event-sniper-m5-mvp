"""
detection_adapter.py

Adapter layer for event detection using OpenAI Responses API.

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


OPENAI_API_URL = "https://api.openai.com/v1/responses"


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


def _safe_fallback(source: str = "fallback") -> Dict[str, Any]:
    return {
        "event_type": "GLOBAL_EVENT",
        "confidence": "LOW",
        "source": source,
        "entities": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def detect(raw_text: str) -> Dict[str, Any]:
    # Guard rail: empty input
    if not raw_text or not raw_text.strip():
        return _safe_fallback(source="empty_input")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _safe_fallback(source="missing_api_key")

    try:
        response = requests.post(
            OPENAI_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "gpt-4.1-mini",
                "input": [
                    {
                        "role": "system",
                        "content": DETECTION_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": raw_text
                    }
                ],
                "temperature": 0,
                "max_output_tokens": 300
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        # ---- ROBUST PARSING (NO ASSUMPTIONS) ----
        output_blocks = data.get("output", [])
        if not output_blocks:
            return _safe_fallback(source="empty_response")

        content_blocks = output_blocks[0].get("content", [])
        if not content_blocks:
            return _safe_fallback(source="empty_content")

        raw_text_out = ""
        for block in content_blocks:
            if isinstance(block, dict) and "text" in block:
                raw_text_out += block["text"]

        raw_text_out = raw_text_out.strip()

        # DEBUG VISIBILITY (VOLUTA)
        print("LLM RAW OUTPUT:", raw_text_out)

        if not raw_text_out:
            return _safe_fallback(source="empty_llm_text")

        return json.loads(raw_text_out)

    except json.JSONDecodeError as e:
        print("JSON PARSE ERROR:", e)
        return _safe_fallback(source="json_parse_error")

    except Exception as e:
        print("DETECTION ERROR:", e)
        return _safe_fallback(source="llm_error")
