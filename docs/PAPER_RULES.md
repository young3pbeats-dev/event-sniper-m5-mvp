# PAPER TRADING RULES

This document defines the rules for paper trading during the MVP phase.

No real funds are used.
No private keys are stored.
No transactions are signed.

---

## 1. Purpose

The purpose of paper trading is to validate:
- event detection quality
- signal timing
- decision discipline

Not profitability.

---

## 2. Assumptions

- Infinite liquidity
- Zero slippage (for MVP only)
- Fixed execution price at signal time

These assumptions are intentionally unrealistic.
They are used to isolate signal quality.

---

## 3. Position Rules

- One position per EVENT
- Fixed notional size (simulated)
- No pyramiding
- No re-entry on the same EVENT

---

## 4. Exit Rules

Each simulated position must define:
- Take Profit (TP)
- Stop Loss (SL)
- Max duration (time-based exit)

First condition hit closes the position.

---

## 5. Evaluation Metrics

Each EVENT produces:
- Entry timestamp
- Exit timestamp
- Max favorable excursion
- Max adverse excursion

Profit is secondary.
Signal behavior is primary.

---

## 6. M5 Device Role

The M5StickC Plus2 acts as:
- visual alert device
- manual confirmation interface
- AUTO / MANUAL mode switch

No execution logic lives on the device.

---

## 7. Upgrade Path

Only after consistent paper results:
- limited capital
- strict caps
- human confirmation

No exceptions.
