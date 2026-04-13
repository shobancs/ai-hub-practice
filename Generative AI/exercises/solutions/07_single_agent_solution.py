"""
Solution: Exercise 7 — Single Agent IT Help Desk Bot
=====================================================
Pattern: SINGLE AGENT
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Mock Database ─────────────────────────────────────────────

EMPLOYEES = {
    "E001": {"name": "Alice Johnson", "email": "alice@company.com", "department": "Engineering", "vpn_active": True},
    "E002": {"name": "Bob Smith", "email": "bob@company.com", "department": "Marketing", "vpn_active": False},
    "E003": {"name": "Carol Davis", "email": "carol@company.com", "department": "HR", "vpn_active": True},
}

KNOWLEDGE_BASE = {
    "vpn": {
        "title": "VPN Troubleshooting",
        "content": "1. Check internet connection. 2. Restart VPN client. 3. Clear VPN cache: Settings > VPN > Clear Cache. 4. If still failing, check if VPN license is active. 5. Contact IT if none of the above work.",
    },
    "password": {
        "title": "Password Reset Guide",
        "content": "Passwords must be: 12+ characters, include uppercase, lowercase, number, and symbol. Reset via: SSO Portal > My Account > Reset Password. Temporary passwords expire in 24 hours.",
    },
    "email": {
        "title": "Email Setup",
        "content": "Use Outlook or Gmail. IMAP: imap.company.com:993. SMTP: smtp.company.com:587. Enable 2FA in Security Settings.",
    },
    "software": {
        "title": "Software Installation",
        "content": "Approved software list: VS Code, Slack, Zoom, Docker, Chrome. Request via IT Portal > Software Request. Admin installs take 24-48 hours.",
    },
    "printer": {
        "title": "Printer Setup",
        "content": "Network printers: Floor2-HP, Floor3-Canon, Floor4-Brother. Add via Settings > Printers > Add Network Printer. Use IP: 192.168.1.x (see printer label).",
    },
}

TICKETS = []

SYSTEM_STATUS = {
    "vpn_server": {"status": "operational", "uptime": "99.9%", "load": "32%"},
    "email_server": {"status": "operational", "uptime": "99.99%", "load": "15%"},
    "sso_portal": {"status": "degraded", "uptime": "98.5%", "load": "78%", "note": "Slow response times"},
    "file_server": {"status": "operational", "uptime": "99.95%", "load": "45%"},
}

# ── Tool Definitions ──────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the IT knowledge base for troubleshooting guides and how-to articles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword (e.g., 'vpn', 'password', 'email')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_employee",
            "description": "Look up employee details by employee ID or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "Employee ID (e.g., 'E001') or name"}
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_system_status",
            "description": "Check the current status of IT systems.",
            "parameters": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "enum": ["vpn_server", "email_server", "sso_portal", "file_server"]}
                },
                "required": ["system"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reset_password",
            "description": "Reset an employee's password and generate a temporary one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID"}
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support ticket for complex issues needing human IT staff.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "employee_id": {"type": "string"}
                },
                "required": ["title", "description", "priority"]
            }
        }
    }
]

# ── Tool Implementations (SOLUTIONS) ─────────────────────────

def search_knowledge_base(query: str) -> str:
    """Search the IT knowledge base."""
    results = []
    for key, article in KNOWLEDGE_BASE.items():
        if query.lower() in key.lower() or query.lower() in article["title"].lower():
            results.append(f"📄 {article['title']}\n{article['content']}")

    if results:
        return "\n\n".join(results)
    return f"No articles found for: '{query}'. Try: vpn, password, email, software, printer."


def lookup_employee(identifier: str) -> str:
    """Look up employee by ID or name."""
    # Check by ID
    if identifier.upper() in EMPLOYEES:
        emp = EMPLOYEES[identifier.upper()]
        return json.dumps({"id": identifier.upper(), **emp}, indent=2)

    # Check by name (partial, case-insensitive)
    for emp_id, emp in EMPLOYEES.items():
        if identifier.lower() in emp["name"].lower():
            return json.dumps({"id": emp_id, **emp}, indent=2)

    return f"Employee not found: '{identifier}'. Available IDs: {', '.join(EMPLOYEES.keys())}"


def check_system_status(system: str) -> str:
    """Check system status."""
    if system in SYSTEM_STATUS:
        info = SYSTEM_STATUS[system]
        result = f"System: {system} | Status: {info['status']} | Uptime: {info['uptime']} | Load: {info['load']}"
        if "note" in info:
            result += f" | Note: {info['note']}"
        return result
    return f"Unknown system: '{system}'. Available: {', '.join(SYSTEM_STATUS.keys())}"


def reset_password(employee_id: str) -> str:
    """Reset employee password."""
    emp_id = employee_id.upper()
    if emp_id not in EMPLOYEES:
        return f"Employee not found: {employee_id}"

    emp = EMPLOYEES[emp_id]
    temp_password = f"TempPass_{emp_id}!2026"
    return (
        f"✅ Password reset successful for {emp['name']} ({emp_id}).\n"
        f"Temporary password: {temp_password}\n"
        f"This password expires in 24 hours. Please change it at SSO Portal > My Account."
    )


def create_ticket(title: str, description: str, priority: str, employee_id: str = None) -> str:
    """Create a support ticket."""
    ticket_id = f"TKT-{len(TICKETS) + 1001}"
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "employee_id": employee_id,
        "created_at": datetime.now().isoformat(),
        "status": "open"
    }
    TICKETS.append(ticket)
    return (
        f"✅ Ticket created!\n"
        f"  ID: {ticket_id}\n"
        f"  Title: {title}\n"
        f"  Priority: {priority.upper()}\n"
        f"  Status: Open\n"
        f"  A human IT specialist will follow up within "
        f"{'1 hour' if priority == 'critical' else '4 hours' if priority == 'high' else '24 hours'}."
    )


TOOL_MAP = {
    "search_knowledge_base": search_knowledge_base,
    "lookup_employee": lookup_employee,
    "check_system_status": check_system_status,
    "reset_password": reset_password,
    "create_ticket": create_ticket,
}

# ── Agent Loop (SOLUTION) ────────────────────────────────────

SYSTEM_PROMPT = """You are HelpBot, the company IT support assistant.

Your capabilities:
- Search the knowledge base for troubleshooting guides
- Look up employee information
- Check system status for outages
- Reset passwords
- Create support tickets for complex issues

Guidelines:
1. Always greet the user warmly
2. Try to diagnose before escalating
3. Check system status if the issue might be system-wide
4. Search the knowledge base for relevant guides
5. Only create a ticket if you cannot resolve the issue
6. Be concise and helpful
"""

def run_agent(user_input: str, max_turns: int = 6) -> str:
    """Run the single-agent loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        messages.append(msg.model_dump())

        # No tool calls → final answer
        if not msg.tool_calls:
            return msg.content

        # Execute each tool call
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            print(f"    🔧 Using tool: {fn_name}({fn_args})")
            result = TOOL_MAP[fn_name](**fn_args)
            print(f"    📋 Result: {result[:100]}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return "I've been working on this for a while. Let me create a ticket for a human specialist."


# ── CLI ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🤖 IT Help Desk Bot (Solution)")
    print("=" * 60)
    print("Type your IT issue. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Goodbye!")
            break
        if not user_input:
            continue

        print()
        response = run_agent(user_input)
        print(f"\n🤖 HelpBot: {response}\n")


if __name__ == "__main__":
    main()
