"""
Real-Time E-Commerce Fraud Detection System
============================================
PATTERN : PARALLEL  (Fan-Out → Fan-In)
SDK     : OpenAI Python SDK (async)
LEVEL   : Intermediate → Advanced

╔══════════════════════════════════════════════════════════════════════════╗
║     REAL-TIME FRAUD DETECTION — PARALLEL AGENT ARCHITECTURE            ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║      📦  INCOMING TRANSACTION                                          ║
║               │                                                        ║
║    ┌──────────┼──────────┬──────────┬──────────┐                      ║
║    ▼          ▼          ▼          ▼          ▼   ← Fan-Out (async)   ║
║ [TXN      [DEVICE    [USER      [PAYMENT   [ITEM                     ║
║  PATTERN]  LOCATION]  BEHAVIOR]  RISK]      RISK]                     ║
║    │          │          │          │          │                       ║
║    └──────────┴──────────┴──────────┴──────────┘                      ║
║                          │                                             ║
║              ┌───────────────────────┐                                 ║
║              │  🛡️  FRAUD DECISION   │  ← Fan-In (aggregator)          ║
║              │      ENGINE           │                                 ║
║              └───────────────────────┘                                 ║
║                          │                                             ║
║              ✅ APPROVE  │  ⚠️ REVIEW  │  🚫 BLOCK                     ║
╚══════════════════════════════════════════════════════════════════════════╝

WHY THIS IS A GREAT PARALLEL USE CASE:
  ✅  Time-critical: fraud decisions must happen in seconds, not minutes
  ✅  Independent dimensions: each risk factor is analysed without needing
      results from other agents
  ✅  Speed = money: blocking a legit customer costs revenue; approving
      fraud costs chargebacks. Parallel analysis minimises decision latency.
  ✅  Ensemble effect: combining 5 specialist perspectives is more accurate
      than any single check

AGENTS (Fan-Out — all 5 run simultaneously):
  Worker 1  Transaction Pattern Analyst  — Amount anomaly, frequency, time-of-day
  Worker 2  Device & Location Analyst    — IP geo, device fingerprint, VPN, proxy
  Worker 3  User Behavior Analyst        — Account age, purchase history, cart flow
  Worker 4  Payment Risk Analyst         — Card type, billing/shipping mismatch, velocity
  Worker 5  Item & Merchant Risk Analyst — High-risk categories, resale value, quantity

AGGREGATOR (Fan-In — runs after all agents complete):
  🛡️  Fraud Decision Engine — Synthesises all 5 risk reports into:
      • Verdict: APPROVE / MANUAL REVIEW / BLOCK
      • Composite risk score (0-100)
      • Confidence level
      • Recommended actions

SETUP:
  pip install -r requirements.txt
  Uses OPENAI_API_KEY from GenAI/.env

RUN:
  python main.py                     ← Interactive: pick a scenario
  python main.py --auto              ← Auto-run all 5 scenarios
  python main.py --scenario 3        ← Run a specific scenario (1-5)
"""

import asyncio
import json
import os
import pathlib
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional

from openai import AsyncOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn

# ─── Load .env from the GenAI parent directory ────────────────────────────────
_env_path = pathlib.Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

console = Console()

# ─── Configuration ────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL          = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA MODEL — Transaction
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Transaction:
    """
    Represents a single e-commerce transaction to be analysed for fraud.
    In production, this would come from a Kafka/SQS queue in real-time.
    """
    transaction_id: str
    timestamp: str
    amount: float
    currency: str
    customer_id: str
    customer_name: str
    account_age_days: int
    email: str
    ip_address: str
    device_type: str
    device_fingerprint: str
    browser: str
    shipping_address: str
    billing_address: str
    card_type: str
    card_last_four: str
    card_issuer_country: str
    items: list[dict] = field(default_factory=list)
    previous_orders_count: int = 0
    previous_orders_total: float = 0.0
    failed_payment_attempts_24h: int = 0
    is_vpn: bool = False
    is_new_device: bool = False
    session_duration_seconds: int = 0
    pages_viewed: int = 0
    cart_changes: int = 0
    promo_code: Optional[str] = None

    def to_summary(self) -> str:
        """Render the transaction as a human-readable summary for agent prompts."""
        items_str = "\n".join(
            f"  - {item['name']} × {item['qty']} @ ${item['price']:.2f}"
            for item in self.items
        )
        return f"""
TRANSACTION ID: {self.transaction_id}
TIMESTAMP:      {self.timestamp}
AMOUNT:         ${self.amount:,.2f} {self.currency}

CUSTOMER:
  Name:           {self.customer_name}
  Customer ID:    {self.customer_id}
  Email:          {self.email}
  Account Age:    {self.account_age_days} days
  Previous Orders:{self.previous_orders_count} (total ${self.previous_orders_total:,.2f})

DEVICE & LOCATION:
  IP Address:     {self.ip_address}
  Device:         {self.device_type}
  Fingerprint:    {self.device_fingerprint}
  Browser:        {self.browser}
  VPN Detected:   {self.is_vpn}
  New Device:     {self.is_new_device}

PAYMENT:
  Card:           {self.card_type} ending {self.card_last_four}
  Issuer Country: {self.card_issuer_country}
  Failed Attempts (24h): {self.failed_payment_attempts_24h}

ADDRESSES:
  Billing:        {self.billing_address}
  Shipping:       {self.shipping_address}

SESSION BEHAVIOR:
  Duration:       {self.session_duration_seconds}s
  Pages Viewed:   {self.pages_viewed}
  Cart Changes:   {self.cart_changes}
  Promo Code:     {self.promo_code or 'None'}

ITEMS:
{items_str}
""".strip()


# ══════════════════════════════════════════════════════════════════════════════
#  TRANSACTION SCENARIOS — Simulated real-time stream
#  Each scenario has different risk characteristics to test the agents
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS: dict[str, Transaction] = {
    "1": Transaction(
        transaction_id="TXN-2026-0304-001",
        timestamp="2026-03-04T10:23:45Z",
        amount=89.99,
        currency="USD",
        customer_id="CUST-78234",
        customer_name="Sarah Johnson",
        account_age_days=847,
        email="sarah.j@gmail.com",
        ip_address="72.134.92.18",
        device_type="iPhone 15 Pro",
        device_fingerprint="fp_ab12cd34ef56",
        browser="Safari 18.2",
        shipping_address="456 Oak Ave, Austin, TX 78701, USA",
        billing_address="456 Oak Ave, Austin, TX 78701, USA",
        card_type="Visa",
        card_last_four="4821",
        card_issuer_country="US",
        items=[
            {"name": "Organic Cotton T-Shirt (M, Navy)", "qty": 2, "price": 34.99},
            {"name": "Bamboo Socks 3-Pack", "qty": 1, "price": 19.99},
        ],
        previous_orders_count=23,
        previous_orders_total=1847.50,
        failed_payment_attempts_24h=0,
        is_vpn=False,
        is_new_device=False,
        session_duration_seconds=420,
        pages_viewed=12,
        cart_changes=2,
    ),
    "2": Transaction(
        transaction_id="TXN-2026-0304-002",
        timestamp="2026-03-04T03:17:22Z",
        amount=4299.00,
        currency="USD",
        customer_id="CUST-99182",
        customer_name="John Williams",
        account_age_days=3,
        email="jwilliams8872@protonmail.com",
        ip_address="185.220.101.42",
        device_type="Windows Desktop",
        device_fingerprint="fp_xx99yy00zz11",
        browser="Chrome 122 (Incognito)",
        shipping_address="Freight Forwarder LLC, 789 Port Blvd, Miami, FL 33132, USA",
        billing_address="15 High Street, London, EC2V 7QN, UK",
        card_type="Mastercard",
        card_last_four="9103",
        card_issuer_country="NG",
        items=[
            {"name": "MacBook Pro 16-inch M4 Max", "qty": 1, "price": 3499.00},
            {"name": "AirPods Pro 3", "qty": 2, "price": 249.00},
            {"name": "Apple Watch Ultra 3", "qty": 1, "price": 799.00},
        ],
        previous_orders_count=0,
        previous_orders_total=0.0,
        failed_payment_attempts_24h=4,
        is_vpn=True,
        is_new_device=True,
        session_duration_seconds=87,
        pages_viewed=3,
        cart_changes=0,
        promo_code="NEWUSER50",
    ),
    "3": Transaction(
        transaction_id="TXN-2026-0304-003",
        timestamp="2026-03-04T14:05:33Z",
        amount=1249.00,
        currency="USD",
        customer_id="CUST-45621",
        customer_name="Maria Garcia",
        account_age_days=412,
        email="maria.garcia@outlook.com",
        ip_address="104.28.45.112",
        device_type="Samsung Galaxy S25",
        device_fingerprint="fp_mn45op67qr89",
        browser="Chrome Mobile 123",
        shipping_address="321 Pine St, Portland, OR 97209, USA",
        billing_address="321 Pine St, Portland, OR 97209, USA",
        card_type="Visa",
        card_last_four="7756",
        card_issuer_country="US",
        items=[
            {"name": "Sony WH-1000XM6 Headphones", "qty": 1, "price": 349.00},
            {"name": "iPad Air M3 256GB", "qty": 1, "price": 699.00},
            {"name": "Anker USB-C Hub", "qty": 1, "price": 49.00},
            {"name": "Screen Protector 2-Pack", "qty": 1, "price": 14.99},
        ],
        previous_orders_count=8,
        previous_orders_total=2340.00,
        failed_payment_attempts_24h=0,
        is_vpn=False,
        is_new_device=True,   # New phone, but existing customer
        session_duration_seconds=1850,
        pages_viewed=34,
        cart_changes=6,
    ),
    "4": Transaction(
        transaction_id="TXN-2026-0304-004",
        timestamp="2026-03-04T02:44:11Z",
        amount=12750.00,
        currency="USD",
        customer_id="CUST-11023",
        customer_name="Alex Petrov",
        account_age_days=1,
        email="a.petrov.shop2026@yandex.ru",
        ip_address="91.243.85.77",
        device_type="Windows Desktop",
        device_fingerprint="fp_gg88hh99ii00",
        browser="Firefox 124",
        shipping_address="Commercial Reshipping Center, 555 Warehouse Row, Carson, CA 90745, USA",
        billing_address="Ulitsa Lenina 42, Moscow 101000, Russia",
        card_type="Visa",
        card_last_four="1234",
        card_issuer_country="RU",
        items=[
            {"name": "iPhone 16 Pro Max 1TB", "qty": 5, "price": 1599.00},
            {"name": "Apple Gift Card $500", "qty": 5, "price": 500.00},
            {"name": "AirPods Max", "qty": 3, "price": 549.00},
        ],
        previous_orders_count=0,
        previous_orders_total=0.0,
        failed_payment_attempts_24h=7,
        is_vpn=True,
        is_new_device=True,
        session_duration_seconds=52,
        pages_viewed=2,
        cart_changes=0,
    ),
    "5": Transaction(
        transaction_id="TXN-2026-0304-005",
        timestamp="2026-03-04T19:30:00Z",
        amount=327.45,
        currency="USD",
        customer_id="CUST-56789",
        customer_name="David Chen",
        account_age_days=1095,
        email="david.chen@company.com",
        ip_address="73.162.88.210",
        device_type="MacBook Pro",
        device_fingerprint="fp_st12uv34wx56",
        browser="Safari 18.2",
        shipping_address="789 Elm Drive, San Jose, CA 95112, USA",
        billing_address="789 Elm Drive, San Jose, CA 95112, USA",
        card_type="Amex",
        card_last_four="3001",
        card_issuer_country="US",
        items=[
            {"name": "Ergonomic Office Chair", "qty": 1, "price": 249.99},
            {"name": "Desk Lamp LED", "qty": 1, "price": 45.99},
            {"name": "Cable Management Kit", "qty": 1, "price": 18.99},
        ],
        previous_orders_count=47,
        previous_orders_total=6720.00,
        failed_payment_attempts_24h=0,
        is_vpn=False,
        is_new_device=False,
        session_duration_seconds=2400,
        pages_viewed=28,
        cart_changes=4,
    ),
}

SCENARIO_LABELS = {
    "1": ("🟢 Legitimate — Regular Customer",    "green"),
    "2": ("🔴 High-Risk — New Account, Suspicious Signals",  "red"),
    "3": ("🟡 Medium-Risk — Existing Customer, New Device",  "yellow"),
    "4": ("🔴 Very High-Risk — Classic Fraud Pattern",       "red"),
    "5": ("🟢 Low-Risk — Loyal Long-term Customer",          "green"),
}


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT SYSTEM PROMPTS
#  Each agent is a specialist fraud analyst examining one risk dimension
# ══════════════════════════════════════════════════════════════════════════════

TRANSACTION_PATTERN_PROMPT = """\
You are a Transaction Pattern Analyst in a real-time fraud detection system.
Analyse the transaction for anomalies in:

1. **Amount Analysis**: Is the amount unusual? Compare to the customer's average order.
   Flag if >3× historical average or >$2000 for new accounts.
2. **Frequency Analysis**: How many orders in what timeframe? Rapid-fire ordering = risk.
3. **Time-of-Day Analysis**: Is this ordered at an unusual hour for the customer's locale?
   Late-night/early-morning purchases carry higher fraud probability.
4. **Order Composition**: Does the item mix make sense? Multiple high-value electronics
   from a first-time buyer = elevated risk.
5. **Promo Code Abuse**: New account + high-value promo code = common fraud vector.

Output format:
- **Risk Signals Found**: List each signal with severity (🔴 High / 🟡 Medium / 🟢 Low)
- **Transaction Pattern Risk Score**: 0-100 (0=safe, 100=certain fraud)
- **One-line Verdict**: Summarise in ≤15 words

Be data-driven. Reference specific numbers from the transaction."""

DEVICE_LOCATION_PROMPT = """\
You are a Device & Location Intelligence Analyst in a real-time fraud detection system.
Analyse the transaction for:

1. **IP Geolocation**: Does the IP location match the billing/shipping country?
   Cross-border mismatches are a strong fraud signal.
2. **VPN / Proxy Detection**: VPN usage during purchase elevates risk, especially
   combined with other signals.
3. **Device Fingerprint**: Is this a known device for this customer?
   New device + new account + high value = high risk.
4. **Browser Analysis**: Incognito mode, unusual user-agent, or known fraud-associated
   browser configurations.
5. **Shipping Destination**: Freight forwarders, PO boxes, and commercial reshipping
   centres are common fraud drop points.

Output format:
- **Risk Signals Found**: List each signal with severity (🔴 High / 🟡 Medium / 🟢 Low)
- **Device & Location Risk Score**: 0-100
- **One-line Verdict**: Summarise in ≤15 words

Be specific about geographic mismatches and device risk factors."""

USER_BEHAVIOR_PROMPT = """\
You are a User Behavior Analyst in a real-time fraud detection system.
Analyse the customer's behavioral patterns:

1. **Account Age & Maturity**: New accounts (<7 days) with high-value purchases
   are a top fraud indicator. Calculate the age-to-spend ratio.
2. **Purchase History**: Does this order fit the customer's buying pattern?
   A sudden 10× jump in order value is suspicious.
3. **Session Behavior**: How long did they browse? How many pages?
   Fraudsters typically have very short sessions (< 2 minutes) with no browsing.
   Legitimate shoppers browse, compare, and modify carts.
4. **Cart Behavior**: Did they add items gradually or dump everything at once?
   Multiple cart changes suggest genuine shopping. Zero changes = suspicious.
5. **Email Quality**: Free/disposable email providers on high-value orders,
   random-looking email addresses, or recently created email patterns.

Output format:
- **Risk Signals Found**: List each signal with severity (🔴 High / 🟡 Medium / 🟢 Low)
- **User Behavior Risk Score**: 0-100
- **One-line Verdict**: Summarise in ≤15 words

Focus on behavioral red flags, not just static profile data."""

PAYMENT_RISK_PROMPT = """\
You are a Payment Risk Analyst in a real-time fraud detection system.
Analyse the payment characteristics:

1. **Card-Country Mismatch**: Does the card issuer country match the billing
   address country? Mismatches are a top-3 fraud indicator.
2. **Billing-Shipping Mismatch**: Different addresses increase risk, especially
   when shipping goes to a different state/country than billing.
3. **Failed Payment Attempts**: Multiple failed attempts in 24 hours before a
   successful one suggests card testing / credential stuffing.
4. **Card Type Risk**: Prepaid cards and certain card types carry higher fraud rates.
5. **Velocity Check**: Multiple orders from same card across different accounts,
   or rapid high-value charges suggest compromised card data.

Output format:
- **Risk Signals Found**: List each signal with severity (🔴 High / 🟡 Medium / 🟢 Low)
- **Payment Risk Score**: 0-100
- **One-line Verdict**: Summarise in ≤15 words

Be precise about which payment mismatches you found and their severity."""

ITEM_RISK_PROMPT = """\
You are an Item & Merchant Risk Analyst in a real-time fraud detection system.
Analyse the items being purchased:

1. **High-Resale Categories**: Electronics, gift cards, luxury goods, and
   designer items are top targets for fraudsters due to easy resale.
   Flag specific items that are high-risk.
2. **Gift Card Red Flag**: Gift card purchases, especially in bulk or combined
   with electronics, are the #1 fraud-targeted category.
3. **Quantity Anomalies**: Multiple units of the same high-value item
   (e.g., 5 iPhones) is a classic fraud pattern.
4. **Item-Customer Fit**: Does the purchase make sense for this customer type?
   A first-time buyer ordering 5 premium phones is suspicious.
5. **Total Basket Value**: High-value baskets on new/young accounts with
   high-resale items = maximum risk.

Output format:
- **Risk Signals Found**: List each signal with severity (🔴 High / 🟡 Medium / 🟢 Low)
- **Item Risk Score**: 0-100
- **One-line Verdict**: Summarise in ≤15 words

Focus on which specific items raise red flags and why."""

FRAUD_DECISION_PROMPT = """\
You are the Chief Fraud Decision Engine for a real-time e-commerce platform.
You receive risk reports from 5 specialist analysts and must render a final verdict
in the format below. Your decision directly controls whether the order is processed,
held for review, or blocked.

DECISION RULES:
- APPROVE:        Composite risk ≤ 30 AND no single agent scored > 60
- MANUAL REVIEW:  Composite risk 31-70 OR any single agent scored 61-85
- BLOCK:          Composite risk > 70 OR any single agent scored > 85
                  OR 3+ agents scored > 50

OUTPUT FORMAT:

## 🛡️ FRAUD DECISION

### Verdict: [APPROVE ✅ / MANUAL REVIEW ⚠️ / BLOCK 🚫]

### Composite Risk Score: [0-100] / 100
(Weighted average: Transaction Pattern 20%, Device & Location 25%, 
User Behavior 20%, Payment Risk 25%, Item Risk 10%)

### Confidence Level: [HIGH / MEDIUM / LOW]

### Risk Breakdown
| Dimension | Score | Key Signal |
|-----------|-------|------------|
(Fill in for all 5 dimensions)

### Top 3 Risk Factors
1. ...
2. ...
3. ...

### Recommended Actions
- If APPROVE: any post-order monitoring needed?
- If MANUAL REVIEW: what should the human reviewer check first?
- If BLOCK: what reason to show the customer? What follow-up actions?

### Decision Rationale
2-3 sentences explaining why this verdict was reached, referencing specific
data points from the analyst reports.

Be decisive. In production, indecision costs money."""


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPER — Call a single agent
# ══════════════════════════════════════════════════════════════════════════════

async def call_agent(
    system_prompt: str,
    user_msg: str,
    label: str,
    style: str,
) -> dict:
    """
    Call the OpenAI chat API with a specialist system prompt.
    Returns a dict with label, content, elapsed time.
    """
    t_start = time.perf_counter()
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.4,   # Lower temp for more deterministic risk scoring
    )
    elapsed = time.perf_counter() - t_start
    text = response.choices[0].message.content

    console.print(Panel(
        text,
        title=f"[{style}]{label}[/{style}]",
        subtitle=f"[dim]{elapsed:.1f}s[/dim]",
        border_style=style,
        padding=(0, 1),
    ))
    return {"label": label, "content": text, "elapsed": elapsed}


# ══════════════════════════════════════════════════════════════════════════════
#  PARALLEL WORKERS — 5 Fraud Detection Specialists
#  Each analyses the SAME transaction from a DIFFERENT risk dimension.
#  All launched simultaneously via asyncio.gather().
# ══════════════════════════════════════════════════════════════════════════════

async def worker_transaction_pattern(txn: Transaction) -> dict:
    """Worker 1 — Transaction pattern analysis (amount, frequency, timing)."""
    console.print("[dim cyan]  ⚡ Transaction Pattern Analyst started[/dim cyan]")
    return await call_agent(
        TRANSACTION_PATTERN_PROMPT,
        f"Analyse this transaction for pattern anomalies:\n\n{txn.to_summary()}",
        "📊 Transaction Pattern Analysis",
        "cyan",
    )


async def worker_device_location(txn: Transaction) -> dict:
    """Worker 2 — Device & location intelligence (IP, VPN, device, geo)."""
    console.print("[dim blue]  ⚡ Device & Location Analyst started[/dim blue]")
    return await call_agent(
        DEVICE_LOCATION_PROMPT,
        f"Analyse this transaction for device/location risks:\n\n{txn.to_summary()}",
        "🌐 Device & Location Intelligence",
        "blue",
    )


async def worker_user_behavior(txn: Transaction) -> dict:
    """Worker 3 — User behavior analysis (account age, session, email)."""
    console.print("[dim yellow]  ⚡ User Behavior Analyst started[/dim yellow]")
    return await call_agent(
        USER_BEHAVIOR_PROMPT,
        f"Analyse this customer's behavioral signals:\n\n{txn.to_summary()}",
        "👤 User Behavior Analysis",
        "yellow",
    )


async def worker_payment_risk(txn: Transaction) -> dict:
    """Worker 4 — Payment risk analysis (card mismatch, velocity, failures)."""
    console.print("[dim red]  ⚡ Payment Risk Analyst started[/dim red]")
    return await call_agent(
        PAYMENT_RISK_PROMPT,
        f"Analyse this transaction's payment risk factors:\n\n{txn.to_summary()}",
        "💳 Payment Risk Analysis",
        "red",
    )


async def worker_item_risk(txn: Transaction) -> dict:
    """Worker 5 — Item & merchant risk (resale value, gift cards, quantities)."""
    console.print("[dim magenta]  ⚡ Item & Merchant Risk Analyst started[/dim magenta]")
    return await call_agent(
        ITEM_RISK_PROMPT,
        f"Analyse the items in this order for fraud risk:\n\n{txn.to_summary()}",
        "📦 Item & Merchant Risk Analysis",
        "magenta",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  AGGREGATOR  (Fan-In — runs after ALL 5 workers complete)
# ══════════════════════════════════════════════════════════════════════════════

async def aggregator_fraud_decision(txn: Transaction, reports: list[dict]) -> str:
    """
    Fan-In: Synthesise all 5 risk reports into a single APPROVE / REVIEW / BLOCK
    decision. Receives the full text of every specialist — has complete context.
    """
    console.print(Rule("🛡️  Fraud Decision Engine — Final Verdict", style="bold white"))

    combined = "\n\n".join(
        f"---\n### {r['label']}\n{r['content']}" for r in reports
    )
    user_msg = (
        f"Transaction Summary:\n{txn.to_summary()}\n\n"
        f"Specialist Risk Reports:\n\n{combined}\n\n"
        "Based on all 5 specialist reports, render your final fraud decision."
    )

    t_start = time.perf_counter()
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": FRAUD_DECISION_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.3,   # Very low temp for consistent decision-making
    )
    elapsed = time.perf_counter() - t_start
    text = response.choices[0].message.content

    console.print(Panel(
        text,
        title="[bold white]🛡️  FRAUD DECISION ENGINE — FINAL VERDICT[/bold white]",
        subtitle=f"[dim]Decision rendered in {elapsed:.1f}s[/dim]",
        border_style="white",
        padding=(0, 1),
    ))
    return text


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE RUNNER — Orchestrates the full parallel fraud detection flow
# ══════════════════════════════════════════════════════════════════════════════

async def run_fraud_detection(txn: Transaction) -> str:
    """
    Execute the full real-time fraud detection pipeline:

        Fan-Out ──► [TxnPattern] [DeviceLocation] [UserBehavior] [PaymentRisk] [ItemRisk]
                                               │
        Fan-In  ──────────────────────────► [Fraud Decision Engine]
                                               │
                                     APPROVE / REVIEW / BLOCK
    """
    # ── Header ────────────────────────────────────────────────────────────────
    items_preview = ", ".join(f"{i['name']}" for i in txn.items[:3])
    if len(txn.items) > 3:
        items_preview += f" +{len(txn.items) - 3} more"

    console.print(Panel.fit(
        f"[bold cyan]🛡️  Real-Time Fraud Detection System[/bold cyan]\n"
        f"[dim]Parallel Agent Pattern — 5 Concurrent Risk Analysts[/dim]\n\n"
        f"Transaction : [bold white]{txn.transaction_id}[/bold white]\n"
        f"Amount      : [bold white]${txn.amount:,.2f} {txn.currency}[/bold white]\n"
        f"Customer    : {txn.customer_name} (ID: {txn.customer_id})\n"
        f"Items       : {items_preview}\n"
        f"Model       : [dim]{MODEL}[/dim]\n"
        f"Agents      : [bold]5 specialist fraud analysts launching concurrently[/bold]",
        border_style="cyan",
    ))

    # ── Transaction details table ─────────────────────────────────────────────
    detail_table = Table(
        title="📋  Transaction Details",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    detail_table.add_column("Field", style="bold")
    detail_table.add_column("Value")

    detail_table.add_row("Transaction ID", txn.transaction_id)
    detail_table.add_row("Timestamp", txn.timestamp)
    detail_table.add_row("Amount", f"${txn.amount:,.2f} {txn.currency}")
    detail_table.add_row("Customer", f"{txn.customer_name} ({txn.email})")
    detail_table.add_row("Account Age", f"{txn.account_age_days} days")
    detail_table.add_row("Previous Orders", f"{txn.previous_orders_count} (${txn.previous_orders_total:,.2f})")
    detail_table.add_row("Device", f"{txn.device_type} / {txn.browser}")
    detail_table.add_row("IP Address", f"{txn.ip_address} (VPN: {txn.is_vpn})")
    detail_table.add_row("Card", f"{txn.card_type} ****{txn.card_last_four} (Issuer: {txn.card_issuer_country})")
    detail_table.add_row("Billing Address", txn.billing_address)
    detail_table.add_row("Shipping Address", txn.shipping_address)
    detail_table.add_row("Session", f"{txn.session_duration_seconds}s / {txn.pages_viewed} pages / {txn.cart_changes} cart changes")
    detail_table.add_row("Failed Payments (24h)", str(txn.failed_payment_attempts_24h))

    console.print(detail_table)

    # ── FAN-OUT: All 5 fraud analysts start simultaneously ────────────────────
    console.print(Rule("⚡  Fan-Out — 5 Fraud Analysts Running in Parallel", style="bold cyan"))

    t_wall_start = time.perf_counter()
    reports: list[dict] = await asyncio.gather(
        worker_transaction_pattern(txn),
        worker_device_location(txn),
        worker_user_behavior(txn),
        worker_payment_risk(txn),
        worker_item_risk(txn),
    )
    t_wall_total = time.perf_counter() - t_wall_start

    # ── Timing summary ────────────────────────────────────────────────────────
    table = Table(
        title="⏱  Parallel Execution Timing",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Agent", style="bold")
    table.add_column("Individual Time", justify="right")

    sequential_total = sum(r["elapsed"] for r in reports)
    for r in reports:
        table.add_row(r["label"], f"{r['elapsed']:.1f}s")

    table.add_row(
        "[bold green]Wall-clock (parallel)[/bold green]",
        f"[bold green]{t_wall_total:.1f}s[/bold green]",
    )
    table.add_row(
        "[dim red]Sequential would take ≈[/dim red]",
        f"[dim red]{sequential_total:.1f}s[/dim red]",
    )
    speedup = sequential_total / t_wall_total if t_wall_total > 0 else 1
    table.add_row(
        "[bold]Speedup[/bold]",
        f"[bold yellow]{speedup:.1f}×[/bold yellow]",
    )
    console.print(table)

    # ── Real-time decision latency highlight ──────────────────────────────────
    if t_wall_total < 10:
        latency_color = "green"
        latency_verdict = "⚡ EXCELLENT — Sub-10s decision latency"
    elif t_wall_total < 20:
        latency_color = "yellow"
        latency_verdict = "⏱️  ACCEPTABLE — Under 20s decision latency"
    else:
        latency_color = "red"
        latency_verdict = "🐌 SLOW — Consider model optimization"

    console.print(Panel(
        f"[{latency_color}]{latency_verdict}\n"
        f"In production, this would run on GPT-4o-mini with streaming for ~2-4s total.[/{latency_color}]",
        title="[bold]Real-Time Performance[/bold]",
        border_style=latency_color,
    ))

    # ── FAN-IN: Aggregator receives all 5 reports ─────────────────────────────
    final = await aggregator_fraud_decision(txn, reports)

    # ── Final render + save ───────────────────────────────────────────────────
    console.print(Rule("📄  FINAL FRAUD DETECTION REPORT", style="bold white"))
    console.print(Markdown(final))
    _save_report(txn, reports, final, t_wall_total)

    return final


def _save_report(
    txn: Transaction,
    reports: list[dict],
    final: str,
    wall_time: float,
) -> None:
    """Persist the full fraud analysis report to a markdown file."""
    output_file = f"fraud_report_{txn.transaction_id.replace('-', '_')}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Fraud Detection Report — {txn.transaction_id}\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Model**: {MODEL}\n")
        f.write(f"**Total Decision Time**: {wall_time:.1f}s (parallel)\n\n")

        f.write("---\n\n## Transaction Summary\n\n")
        f.write(f"```\n{txn.to_summary()}\n```\n\n")

        f.write("---\n\n## Specialist Analyst Reports\n\n")
        for r in reports:
            f.write(f"### {r['label']} ({r['elapsed']:.1f}s)\n\n{r['content']}\n\n---\n\n")

        f.write("## Final Fraud Decision\n\n")
        f.write(final)

    console.print(f"\n[dim]💾  Report saved to [bold]{output_file}[/bold][/dim]")


# ══════════════════════════════════════════════════════════════════════════════
#  BATCH MODE — Process multiple transactions (simulated real-time stream)
# ══════════════════════════════════════════════════════════════════════════════

async def run_batch_stream(scenario_keys: list[str]) -> None:
    """
    Simulate a real-time transaction stream by processing multiple
    transactions sequentially (each transaction is analysed in parallel).
    """
    console.print(Panel.fit(
        f"[bold cyan]📡 Real-Time Transaction Stream[/bold cyan]\n"
        f"[dim]Processing {len(scenario_keys)} transactions sequentially\n"
        f"Each transaction analysed by 5 parallel agents[/dim]",
        border_style="cyan",
    ))

    results = []
    for i, key in enumerate(scenario_keys, 1):
        txn = SCENARIOS[key]
        label, color = SCENARIO_LABELS[key]
        console.print(Rule(
            f"Transaction {i}/{len(scenario_keys)}: {label}",
            style=f"bold {color}",
        ))
        verdict = await run_fraud_detection(txn)
        results.append((txn, label, verdict))
        if i < len(scenario_keys):
            console.print("\n[dim]⏳  Next transaction arriving...[/dim]\n")
            await asyncio.sleep(1)

    # ── Summary table ─────────────────────────────────────────────────────────
    console.print(Rule("📊  Batch Processing Summary", style="bold cyan"))
    summary = Table(
        title="Transaction Verdicts",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    summary.add_column("Transaction ID", style="bold")
    summary.add_column("Amount", justify="right")
    summary.add_column("Scenario")
    summary.add_column("Customer")

    for txn, label, _ in results:
        summary.add_row(
            txn.transaction_id,
            f"${txn.amount:,.2f}",
            label,
            txn.customer_name,
        )
    console.print(summary)


# ══════════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

async def main() -> None:
    console.print(
        "\n[bold]🛡️  Real-Time E-Commerce Fraud Detection System[/bold]\n"
        "[dim]Parallel Agent Pattern | 5 Concurrent Fraud Analysts per Transaction[/dim]\n"
    )

    # ── Check for CLI args ────────────────────────────────────────────────────
    if "--auto" in sys.argv:
        await run_batch_stream(list(SCENARIOS.keys()))
        return

    for arg in sys.argv:
        if arg.startswith("--scenario"):
            key = arg.split("=")[-1] if "=" in arg else (
                sys.argv[sys.argv.index(arg) + 1] if sys.argv.index(arg) + 1 < len(sys.argv) else "1"
            )
            if key in SCENARIOS:
                await run_fraud_detection(SCENARIOS[key])
                return
            console.print(f"[red]Unknown scenario: {key}[/red]")

    # ── Interactive menu ──────────────────────────────────────────────────────
    console.print("[bold]Transaction Scenarios:[/bold]\n")

    for key in SCENARIOS:
        txn = SCENARIOS[key]
        label, color = SCENARIO_LABELS[key]
        items_count = sum(i["qty"] for i in txn.items)
        console.print(
            f"  [cyan]{key}[/cyan].  [{color}]{label}[/{color}]\n"
            f"      ${txn.amount:,.2f} | {txn.customer_name} | "
            f"{items_count} items | Account: {txn.account_age_days} days old"
        )
    console.print(f"\n  [cyan]A[/cyan].  [bold]Run ALL scenarios[/bold] (batch stream mode)\n")

    console.print("[dim]Each scenario runs 5 parallel fraud detection agents + aggregator.[/dim]\n")
    choice = input("Select (1-5 or A): ").strip().upper()

    if choice == "A":
        await run_batch_stream(list(SCENARIOS.keys()))
    elif choice in SCENARIOS:
        await run_fraud_detection(SCENARIOS[choice])
    else:
        console.print(f"[yellow]Invalid choice '{choice}'. Running scenario 2 (high-risk).[/yellow]")
        await run_fraud_detection(SCENARIOS["2"])


if __name__ == "__main__":
    asyncio.run(main())
