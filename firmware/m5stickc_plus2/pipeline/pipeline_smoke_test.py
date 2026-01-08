"""
pipeline_smoke_test.py

Minimal end-to-end smoke test for the event pipeline.
Purpose: validate Detection → Filtering → Payload flow.
"""

from event_contract import process_raw_text, reset_state

TEST_CASES = [
    # Noise (must be rejected)
    "Bitcoin is pumping today",

    # Trump first-class source (must pass)
    "Trump announces new tariffs on Chinese imports effective immediately",

    # Duplicate (must be rejected)
    "Trump announces new tariffs on Chinese imports effective immediately",

    # Global but ambiguous (likely MEDIUM → rejected)
    "US officials discuss potential future policy changes",

    # Clear geopolitical escalation (must pass)
    "NATO responds to increased military activity by Russia in Eastern Europe"
]


if __name__ == "__main__":
    print("=== PIPELINE SMOKE TEST ===\n")
    reset_state()

    for i, text in enumerate(TEST_CASES, start=1):
        print(f"Test {i}: {text}")
        result = process_raw_text(text)
        print("Output:", result)
        print("-" * 40)

print("\n=== FORCED EVENT TEST ===")

forced_event = {
    "event_type": "POLITICAL_STATEMENT",
    "confidence": "HIGH",
    "source": "POLITICAL_STATEMENT",
    "entities": ["TRUMP", "CHINA"]
}

from event_contract import process_event
print(process_event(forced_event))
