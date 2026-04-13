"""
Solution: Tool Use — Personal Finance Assistant
=================================================
Pattern: TOOL USE (Chapter 5)

Complete solution with all TODOs implemented.
"""

import json, os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ═══════════════════════════════════════════════════════════
#  MOCK DATA
# ═══════════════════════════════════════════════════════════

ACCOUNT = {"balance": 5000.00}

TRANSACTIONS = [
    {"date": "2026-03-01", "type": "income",  "category": "salary",       "description": "Monthly salary",    "amount": 5000.00},
    {"date": "2026-03-02", "type": "expense", "category": "rent",         "description": "Apartment rent",    "amount": 1500.00},
    {"date": "2026-03-03", "type": "expense", "category": "groceries",    "description": "Weekly groceries",  "amount": 85.50},
    {"date": "2026-03-04", "type": "expense", "category": "transport",    "description": "Uber rides",        "amount": 45.00},
    {"date": "2026-03-05", "type": "expense", "category": "dining",       "description": "Dinner with friends","amount": 62.00},
    {"date": "2026-03-05", "type": "expense", "category": "subscription", "description": "Netflix + Spotify", "amount": 25.00},
]

BUDGETS = {
    "groceries": 400,
    "dining": 200,
    "transport": 150,
    "subscription": 50,
    "entertainment": 100,
}


# ═══════════════════════════════════════════════════════════
#  TOOL DEFINITIONS
# ═══════════════════════════════════════════════════════════

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Get the current account balance.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_transaction",
            "description": "Add a new expense or income transaction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type":        {"type": "string", "enum": ["income", "expense"]},
                    "category":    {"type": "string", "description": "e.g. groceries, dining, salary"},
                    "description": {"type": "string"},
                    "amount":      {"type": "number"},
                },
                "required": ["type", "category", "description", "amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_summary",
            "description": "Get a summary of spending grouped by category for the current month.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_budget",
            "description": "Check spending vs budget limit for a category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_transactions",
            "description": "List recent transactions, optionally filtered by category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Optional category filter"},
                    "limit":    {"type": "integer", "description": "Max transactions to return (default 10)"},
                },
            },
        },
    },
]


# ═══════════════════════════════════════════════════════════
#  TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════

def get_balance() -> str:
    return f"💰 Current balance: ${ACCOUNT['balance']:.2f}"


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 1: Add Transaction
# ═══════════════════════════════════════════════════════════

def add_transaction(type: str, category: str, description: str, amount: float) -> str:
    """Add a transaction and update the balance."""
    # Edge case: check if expense exceeds balance
    if type == "expense" and amount > ACCOUNT["balance"]:
        return (
            f"❌ Insufficient funds! Balance: ${ACCOUNT['balance']:.2f}, "
            f"Attempted: ${amount:.2f}"
        )

    # Create the transaction
    txn = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": type,
        "category": category.lower(),
        "description": description,
        "amount": amount,
    }
    TRANSACTIONS.append(txn)

    # Update balance
    if type == "income":
        ACCOUNT["balance"] += amount
    else:
        ACCOUNT["balance"] -= amount

    icon = "📈" if type == "income" else "📉"
    return (
        f"{icon} Transaction added!\n"
        f"  Type: {type}\n"
        f"  Category: {category}\n"
        f"  Description: {description}\n"
        f"  Amount: ${amount:.2f}\n"
        f"  New balance: ${ACCOUNT['balance']:.2f}"
    )


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 2: Spending Summary
# ═══════════════════════════════════════════════════════════

def get_spending_summary() -> str:
    """Calculate total spending per category."""
    summary = {}
    for txn in TRANSACTIONS:
        if txn["type"] == "expense":
            cat = txn["category"]
            summary[cat] = summary.get(cat, 0) + txn["amount"]

    # Sort by amount (highest first)
    sorted_cats = sorted(summary.items(), key=lambda x: x[1], reverse=True)

    lines = ["📊 Spending Summary:"]
    total = 0
    for cat, amount in sorted_cats:
        lines.append(f"  {cat:15s} : ${amount:>8,.2f}")
        total += amount

    lines.append(f"  {'─' * 28}")
    lines.append(f"  {'TOTAL':15s} : ${total:>8,.2f}")

    return "\n".join(lines)


def check_budget(category: str) -> str:
    """Check if spending in a category exceeds its budget. (PROVIDED)"""
    cat = category.lower()
    if cat not in BUDGETS:
        return f"No budget set for '{category}'. Set budgets: {', '.join(BUDGETS.keys())}"

    spent = sum(t["amount"] for t in TRANSACTIONS if t["type"] == "expense" and t["category"] == cat)
    budget = BUDGETS[cat]
    remaining = budget - spent
    pct = (spent / budget) * 100

    status = "✅ Under budget" if remaining > 0 else "🚨 OVER BUDGET"
    return (
        f"Category: {cat}\n"
        f"Budget: ${budget:.2f}\n"
        f"Spent: ${spent:.2f} ({pct:.0f}%)\n"
        f"Remaining: ${remaining:.2f}\n"
        f"Status: {status}"
    )


def list_transactions(category: str = None, limit: int = 10) -> str:
    """List recent transactions. (PROVIDED)"""
    txns = TRANSACTIONS
    if category:
        txns = [t for t in txns if t["category"] == category.lower()]

    txns = txns[-limit:]
    if not txns:
        return "No transactions found."

    lines = []
    for t in txns:
        icon = "📈" if t["type"] == "income" else "📉"
        lines.append(f"  {icon} {t['date']} | {t['category']:12s} | {t['description']:20s} | ${t['amount']:.2f}")
    return "\n".join(lines)


TOOL_MAP = {
    "get_balance": get_balance,
    "add_transaction": add_transaction,
    "get_spending_summary": get_spending_summary,
    "check_budget": check_budget,
    "list_transactions": list_transactions,
}


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 3: AGENT LOOP
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are FinBot 💰, a personal finance assistant.

You help users:
- Track income and expenses
- Check their balance
- View spending summaries
- Monitor budget limits
- List recent transactions

Guidelines:
- Be concise and clear with financial info
- Warn users when they're close to or over budget
- Suggest savings tips when appropriate
- Always confirm after adding a transaction
"""


def run_agent(user_input: str, conversation: list, max_turns: int = 6) -> str:
    """Complete the agent tool-calling loop."""
    conversation.append({"role": "user", "content": user_input})

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            tools=TOOLS,
        )

        msg = response.choices[0].message
        conversation.append(msg)

        # No tool calls → final answer
        if not msg.tool_calls:
            return msg.content

        # Process each tool call
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            print(f"  🔧 Calling: {fn_name}({fn_args})")

            fn = TOOL_MAP.get(fn_name)
            if fn:
                result = fn(**fn_args)
            else:
                result = f"Unknown tool: {fn_name}"

            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "I reached my processing limit. Please try a simpler request."


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

SAMPLE_QUERIES = [
    "What's my current balance?",
    "I spent $45 on groceries today at Whole Foods",
    "Show me my spending summary",
    "Am I over budget on dining?",
    "List my recent transactions",
]


def main():
    print("=" * 60)
    print("💰 FinBot — Personal Finance Assistant")
    print("=" * 60)
    print("\nSample queries:")
    for i, q in enumerate(SAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print("\nType 'quit' to exit.\n")

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Stay on budget! Bye!")
            break
        if not user_input:
            continue

        print()
        response = run_agent(user_input, conversation)
        print(f"FinBot: {response}\n")


if __name__ == "__main__":
    main()
