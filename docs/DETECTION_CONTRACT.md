# Detection Contract

## Purpose
Define what qualifies as an EVENT at the detection stage.
Detection precedes filtering and human confirmation.

## What Detection IS
- Emergence of a new global narrative
- Sudden political or macro announcement
- Geopolitical escalation or stance change
- High-ambiguity news with global actors involved

## What Detection IS NOT
- Static keywords
- Single tweets without amplification
- Local news
- Already-mature narratives
- Token-level signals

## Allowed Sources

* Major global news outlets
* Official political statements
* Government / central bank communications
* Aggregated geopolitical feeds

### Primary Social Sources (High-Priority)

* Donald J. Trump – Truth Social (official account)
* Donald J. Trump – X / Twitter (official account)
* Verified social accounts directly controlled by Donald J. Trump

Notes:

* Trump social posts are treated as **first-class detection signals**
* No engagement threshold required if the source is direct and verified
* Interpretation is deferred to later stages (filtering / confirmation)


## Detection Output (Required)
```json
{
  "event_type": "POLITICAL_STATEMENT | GLOBAL_EVENT | MACRO_SHOCK",
  "confidence": "LOW | MEDIUM | HIGH",
  "source": "string",
  "entities": ["string"],
  "timestamp": "ISO-8601"
}
