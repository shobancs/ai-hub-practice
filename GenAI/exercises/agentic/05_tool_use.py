"""
Exercise: Tool Use — Personal Finance Assistant
=================================================
Pattern: TOOL USE (Chapter 5)

GOAL:
  Build an agent with tools to manage a personal budget:
    - Check account balance
    - Add expense / income transactions
    - Get spending summary by category
    - Set and check budget limits
    - Convert currencies

YOUR TASKS:
  1. Implement add_transaction()            (TODO 1)
  2. Implement get_spending_summary()       (TODO 2)
  3. Complete the agent loop                (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 05_tool_use.py
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


def add_transaction(type: str, category: str, description: str, amount: float) -> str:
    """
    TODO 1: Add a transaction and update the balance.

    Steps:
    1. Create a transaction dict with: date (today), type, category, description, amount
    2. Append it to TRANSACTIONS list
    3. Update ACCOUNT["balance"]:
       - If type == "income": add amount
       - If type == "expense": subtract amount
    4. Return a confirmation string with the details

    Edge case: If expense amount > balance, return an error message.
    """
    # YOUR CODE HERE
    pass


def get_spending_summary() -> str:
    """
    TODO 2: Calculate total spending per category.

    Steps:
    1. Loop through TRANSACTIONS
    2. For each expense, add its amount to that category's total
    3. Sort categories by total (highest first)
    4. Build a formatted string showing each category and its total
    5. Include the grand total at the bottom

    Example output:
      📊 Spending Summary:
        rent          : $1,500.00
        groceries     : $  85.50
        dining        : $  62.00
        ...
        ────────────────────
        TOTAL         : $1,717.50
    """
    # YOUR CODE HERE
    pass


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
#  AGENT LOOP
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
    """
    TODO 3: Complete the agent tool-calling loop.

    Steps:
    1. Append the user message to conversation
    2. Loop up to max_turns:
       a. Call client.chat.completions.create() with model, conversation, tools
       b. Get the response message
       c. Append it to conversation
       d. If NO tool calls → return the text content (final answer)
       e. If tool calls → for each tool call:
          - Parse function name and arguments
          - Call the function from TOOL_MAP
          - Append the tool result to conversation
    3. If max turns reached, return a fallback message

    Hint: Look at the ticket_booking_agent.py for reference.
    """
    # YOUR CODE HERE
    pass


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
        if response is None:
            print("❌ TODO 3 not implemented yet!\n")
        else:
            print(f"💰 FinBot: {response}\n")


if __name__ == "__main__":
    main()
