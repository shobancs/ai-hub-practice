# 🛡️ Real-Time E-Commerce Fraud Detection System

> **Pattern**: Parallel (Fan-Out → Fan-In)
> **Level**: Intermediate → Advanced
> **SDK**: OpenAI Python SDK (async)
> **Use Case**: Real-time fraud detection for e-commerce transactions

---

## Why This Use Case?

Fraud detection is one of the **best real-world applications** of the parallel agent pattern because:

| Requirement | Why Parallel Wins |
|---|---|
| **Time-critical** | Fraud decisions must happen in seconds — customers abandon checkout after 3s of waiting |
| **Independent dimensions** | Transaction patterns, device signals, user behavior, payment risk, and item risk are analysed independently |
| **Speed = Money** | Blocking legit customers costs revenue; approving fraud costs chargebacks. Parallel cuts decision time by 3-5× |
| **Ensemble accuracy** | 5 specialist perspectives catch more fraud than any single check |

---

## Architecture

```
     📦  INCOMING TRANSACTION
              │
   ┌──────────┼──────────┬──────────┬──────────┐
   ▼          ▼          ▼          ▼          ▼      ← Fan-Out (async)
[TXN       [DEVICE    [USER      [PAYMENT   [ITEM
 PATTERN]   LOCATION]  BEHAVIOR]  RISK]      RISK]
   │          │          │          │          │
   └──────────┴──────────┴──────────┴──────────┘
                         │
             ┌───────────────────────┐
             │  🛡️  FRAUD DECISION    │  ← Fan-In (aggregator)
             │      ENGINE           │
             └───────────────────────┘
                         │
             ✅ APPROVE  ⚠️ REVIEW  🚫 BLOCK
```

All 5 specialist agents launch **simultaneously** via `asyncio.gather()`.
The Fraud Decision Engine runs only **after all agents complete**, with full
context from every risk report.

---

## Agents

### Fan-Out Workers (5 parallel specialists)

| Agent | Focus | Key Signals |
|---|---|---|
| 📊 **Transaction Pattern** | Amount, frequency, time-of-day | Unusual amounts, 3 AM purchases, rapid-fire orders |
| 🌐 **Device & Location** | IP, VPN, device fingerprint, geo | Cross-border mismatches, VPN + new device, freight forwarders |
| 👤 **User Behavior** | Account age, session, purchase history | New account + high spend, 52-second session, no browsing |
| 💳 **Payment Risk** | Card mismatch, velocity, failures | Card country ≠ billing country, 7 failed attempts, address mismatch |
| 📦 **Item & Merchant Risk** | Resale value, gift cards, quantity | 5× iPhones, gift cards in bulk, $12K first order |

### Fan-In Aggregator

| Agent | Output |
|---|---|
| 🛡️ **Fraud Decision Engine** | **APPROVE** ✅ / **MANUAL REVIEW** ⚠️ / **BLOCK** 🚫 + composite risk score (0-100) |

---

## Project Structure

```
realtime_fraud_detection/
├── main.py          ← Full application: models, scenarios, agents, aggregator, CLI
├── requirements.txt ← openai, python-dotenv, rich
├── .env.example     ← Env var reference (actual .env lives in GenAI/)
└── README.md        ← This file
```

---

## Quick Start

```bash
cd GenAI/examples/realtime_fraud_detection

# Use existing venv or create one
pip install -r requirements.txt

# Interactive mode — pick a scenario
python main.py

# Run a specific scenario
python main.py --scenario 2

# Run all 5 scenarios (batch stream mode)
python main.py --auto
```

> **Auth**: Reads `OPENAI_API_KEY` from `GenAI/.env` automatically.

---

## Transaction Scenarios

The system includes 5 pre-built transaction scenarios covering the full risk spectrum:

### Scenario 1: 🟢 Legitimate — Regular Customer
| Field | Value |
|---|---|
| Amount | $89.99 |
| Customer | Sarah Johnson (account: 847 days, 23 prior orders) |
| Items | Cotton T-Shirts, Bamboo Socks |
| Risk Signals | None — matching addresses, known device, normal browsing |
| Expected Verdict | **APPROVE** ✅ |

### Scenario 2: 🔴 High-Risk — New Account, Suspicious Signals
| Field | Value |
|---|---|
| Amount | $4,299.00 |
| Customer | John Williams (account: 3 days, 0 prior orders) |
| Items | MacBook Pro, AirPods Pro ×2, Apple Watch Ultra |
| Risk Signals | VPN, incognito browser, freight forwarder address, 4 failed payments, card from Nigeria |
| Expected Verdict | **BLOCK** 🚫 |

### Scenario 3: 🟡 Medium-Risk — Existing Customer, New Device
| Field | Value |
|---|---|
| Amount | $1,249.00 |
| Customer | Maria Garcia (account: 412 days, 8 prior orders) |
| Items | Sony Headphones, iPad Air, Accessories |
| Risk Signals | New device (but long account history, extensive browsing) |
| Expected Verdict | **MANUAL REVIEW** ⚠️ or **APPROVE** ✅ |

### Scenario 4: 🔴 Very High-Risk — Classic Fraud Pattern
| Field | Value |
|---|---|
| Amount | $12,750.00 |
| Customer | Alex Petrov (account: 1 day, 0 prior orders) |
| Items | 5× iPhone 16 Pro Max, 5× $500 Gift Cards, 3× AirPods Max |
| Risk Signals | Every red flag — new account, VPN, billing/shipping country mismatch (Russia/US), reshipping center, 7 failed payments, gift cards, bulk electronics, 52-second session |
| Expected Verdict | **BLOCK** 🚫 (immediate) |

### Scenario 5: 🟢 Low-Risk — Loyal Long-term Customer
| Field | Value |
|---|---|
| Amount | $327.45 |
| Customer | David Chen (account: 1,095 days, 47 prior orders) |
| Items | Office Chair, Desk Lamp, Cable Kit |
| Risk Signals | None — 3-year customer, known device, long session, matching addresses |
| Expected Verdict | **APPROVE** ✅ |

---

## Sample Output

When you run a scenario, the system produces:

1. **Transaction Details Table** — All fields at a glance
2. **5 Parallel Risk Reports** — Each specialist's findings with risk scores and signals
3. **Timing Table** — Wall-clock vs sequential time with speedup multiplier
4. **Real-Time Latency Assessment** — Performance grade for production readiness
5. **Final Fraud Decision** — APPROVE / MANUAL REVIEW / BLOCK with:
   - Composite risk score (0-100)
   - Confidence level
   - Risk breakdown table
   - Top 3 risk factors
   - Recommended actions
   - Decision rationale
6. **Saved Report** — Full markdown report saved to `fraud_report_TXN_*.md`

---

## How It Maps to Production

| Demo Component | Production Equivalent |
|---|---|
| Transaction dataclass | Kafka/SQS event payload |
| `asyncio.gather()` | Parallel microservice calls or serverless functions |
| OpenAI API call | Specialised ML models (XGBoost, neural nets) + rules engine |
| Rich console output | Real-time dashboard (Grafana, DataDog) |
| Markdown report | Event store + audit trail (for compliance) |
| Interactive CLI | API endpoint (`POST /api/v1/fraud-check`) |

---

## Key Concepts Demonstrated

### 1. Fan-Out / Fan-In Pattern
All 5 agents start at the **exact same instant**. The wall-clock time equals the
slowest single agent, not the sum of all 5.

### 2. Specialist Agent Design
Each agent has a **focused system prompt** that constrains its analysis to one
risk dimension. This produces more thorough analysis than a single generalist agent.

### 3. Structured Aggregation
The Fraud Decision Engine follows **explicit decision rules** (risk thresholds)
to translate specialist reports into an actionable verdict.

### 4. Real-Time Decision Latency
With `gpt-4o-mini`, the full 5-agent + aggregator pipeline typically completes
in **4-8 seconds** — fast enough for real-time e-commerce checkout flows.

### 5. Simulated Transaction Stream
Batch mode (`--auto`) demonstrates processing a **stream** of transactions,
mimicking a production fraud detection queue.

---

## Extending This Example

- **Add a 6th agent**: Email reputation checker (disposable email detection)
- **Add human-in-the-loop**: When verdict = MANUAL REVIEW, prompt for human decision
- **Streaming responses**: Use OpenAI streaming to show risk assessments as they arrive
- **Webhook integration**: Wrap in FastAPI to accept real transaction payloads
- **Historical learning**: Feed past fraud decisions back as few-shot examples
- **Threshold tuning**: Make risk thresholds configurable via environment variables

---

## Related Patterns

| Pattern | When to Use Instead |
|---|---|
| **Sequential** | When risk assessments depend on each other (e.g., device check must pass before payment check) |
| **Routing** | When you want to skip certain checks based on transaction amount or customer tier |
| **Reflection** | When the fraud decision should be self-critiqued before finalising |
| **Multi-Agent** | When agents need to debate (e.g., one says BLOCK, another says APPROVE — they negotiate) |
