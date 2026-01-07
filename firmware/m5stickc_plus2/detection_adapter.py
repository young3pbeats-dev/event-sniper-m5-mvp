import json
import os
import requests
from datetime import datetime, timezone

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

DETECTION_SYSTEM_PROMPT = """
You are a DETECTION module.

You must output ONLY valid JSON.
No explanations. No markdown.

Allowed values:

event_type:
- POLITICAL_STATEMENT
- GLOBAL_EVENT
- MACRO_SHOCK

confidence:
- LOW
- MEDIUM
- HIGH

source MUST be one of:
- TRUMP_STATEMENT
- GLOBAL_NEWS
- GEOPOLITICS
- OFFICIAL_RELEASE

Rules:
- If Trump is the speaker → source = TRUMP_STATEMENT
- Do NOT invent new source labels
- Be conservative: HIGH only for clear global-impact events

JSON schema:
{
  "event_type": "...",
  "confidence": "...",
  "source": "...",
  "entities": ["..."],
  "timestamp": "ISO-8601"
}
"""


def detect(raw_text: str) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")

    # HARD GUARD — niente fallback silenziosi
    if not api_key or not api_key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY NOT LOADED INSIDE detection_adapter")

    response = requests.post(
        OPENAI_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": DETECTION_SYSTEM_PROMPT},
                {"role": "user", "content": raw_text},
            ],
            "temperature": 0,
            "max_tokens": 300,
        },
        timeout=20,
    )

    if response.status_code != 200:
        raise RuntimeError(f"OPENAI HTTP ERROR {response.status_code}: {response.text}")

    content = response.json()["choices"][0]["message"]["content"]
    result = json.loads(content)

if "trump" in raw_text.lower():
    result["source"] = "TRUMP_STATEMENT"
  
  ALLOWED_SOURCES = {
    "TRUMP_STATEMENT",
    "GLOBAL_NEWS",
    "GEOPOLITICS",
    "OFFICIAL_RELEASE",
}

if result.get("source") not in ALLOWED_SOURCES:
    raise RuntimeError(f"INVALID SOURCE FROM MODEL: {result.get('source')}")


    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return result
