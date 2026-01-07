# HARD RULE:
# OpenAI Responses API is the ONLY supported detection backend.
# Claude / Anthropic is explicitly unsupported.

import json
import os
import requests
from datetime import datetime, timezone

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

DETECTION_SYSTEM_PROMPT = """
You must output ONLY valid JSON.

{
  "event_type": "POLITICAL_STATEMENT | GLOBAL_EVENT | MACRO_SHOCK",
  "confidence": "LOW | MEDIUM | HIGH",
  "source": "string",
  "entities": ["string"],
  "timestamp": "ISO-8601"
}

CONFIDENCE RULES:
- HIGH: Clear emergence of new global-level event involving nations, global leaders, institutions, wars, sanctions, treaties, or systemic macro decisions
- MEDIUM: Ambiguous or early signals involving global actors
- LOW: Weak, incomplete, non-global signals

ENTITY RULES:
- Include ONLY explicitly mentioned global actors (countries, heads of state, governments, institutions, central banks)
- Do NOT infer or invent entities

PRIMARY SOCIAL SOURCES:
- Donald J. Trump social posts are FIRST-CLASS detection signals
- Mark as source: "POLITICAL_STATEMENT" for Trump content
- Mark as source: "GLOBAL_NEWS" for news articles
- Mark as source: "GEOPOLITICS" for geopolitical analysis

EVENT TYPES:
- POLITICAL_STATEMENT: Direct statements from political figures
- GLOBAL_EVENT: Geopolitical developments, wars, sanctions
- MACRO_SHOCK: Economic policy, central bank decisions, systemic changes
"""

def _safe_fallback(source="fallback"):
    return {
        "event_type": "GLOBAL_EVENT",
        "confidence": "LOW",
        "source": source,
        "entities": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def detect(raw_text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _safe_fallback("missing_api_key")

    try:
      response = requests.post(
    OPENAI_API_URL,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": DETECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text}
                ],
                "max_tokens": 300,
                "temperature": 0
            },
            timeout=20
        )
      
      if response.status_code != 200:
    print("OPENAI STATUS:", response.status_code)
    print("OPENAI ERROR:", response.text)
    return _safe_fallback(source="openai_http_error")
        
        response.raise_for_status()
        data = response.json()
        
        text = data["choices"][0]["message"]["content"]
        
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        result = json.loads(text)
        
        required_fields = ["event_type", "confidence", "source", "entities", "timestamp"]
        if not all(field in result for field in required_fields):
            return _safe_fallback("invalid_schema")
        
        return result
        
    except requests.exceptions.RequestException:
        return _safe_fallback("network_error")
    except json.JSONDecodeError:
        return _safe_fallback("parse_error")
    except Exception:
        return _safe_fallback("unknown_error")
```

---

## 🎯 WHY IT WAS BROKEN

| Component | Before | After | Impact |
|-----------|--------|-------|--------|
| **API URL** | `/v1/responses` (doesn't exist) | `/v1/chat/completions` | API call was failing |
| **Model** | `gpt-4.1-mini` (fake) | `gpt-4` | Invalid model = error |
| **Request** | `"input": raw_text` | `"messages": [...]` | Wrong structure = error |
| **Response** | `data["output"][0]...` | `data["choices"][0]...` | Parse failed = fallback |
| **Fallback** | Returns LOW confidence | Gets rejected by filter | Always None |

---

## ✅ EXPECTED BEHAVIOR AFTER FIX
```
Test 1: Bitcoin is pumping today
Output: None  ← Correctly rejected (not global-scale)

Test 2: Trump announces new tariffs on Chinese imports
Output: {'event_type': 'POLITICAL_STATEMENT', 'confidence': 'HIGH', 'symbol': 'TRUMP/CHINA'}  ← ACCEPTED

Test 3: (duplicate)
Output: None  ← Correctly rejected (anti-spam)

Test 4: US officials discuss potential future policy changes
Output: None  ← Correctly rejected (ambiguous, not concrete)

Test 5: NATO responds to Russia military activity
Output: {'event_type': 'GLOBAL_EVENT', 'confidence': 'HIGH', 'symbol': 'NATO/RUSSIA'}  ← ACCEPTED
