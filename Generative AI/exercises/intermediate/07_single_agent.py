"""
Exercise 7: Single Agent — IT Help Desk Bot
============================================
Difficulty: ⭐⭐ Intermediate
Time: 60-90 minutes
Pattern: SINGLE AGENT

GOAL:
  Build an IT help desk agent that uses tools to diagnose and resolve
  common tech issues (password resets, VPN problems, software installs).

YOUR TASKS:
  1. Implement the missing tool functions (marked with TODO)
  2. Complete the agent loop in run_agent()
  3. Test with the sample queries at the bottom

CONCEPTS:
  - OpenAI function calling (tool use)
  - Agent loop (think → act → observe)
  - Tool result handling
  - Conversation memory

SETUP:
  pip install openai python-dotenv

RUN:
  python 07_single_agent.py
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ╔══════════════════════════════════════════════════════════════╗
# ║  MOCK DATABASE — Simulates your company's IT systems        ║
# ╚══════════════════════════════════════════════════════════════╝

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

TICKETS = []  # Stores created tickets

SYSTEM_STATUS = {
    "vpn_server": {"status": "operational", "uptime": "99.9%", "load": "32%"},
    "email_server": {"status": "operational", "uptime": "99.99%", "load": "15%"},
    "sso_portal": {"status": "degraded", "uptime": "98.5%", "load": "78%", "note": "Slow response times"},
    "file_server": {"status": "operational", "uptime": "99.95%", "load": "45%"},
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  TOOL DEFINITIONS — Tell the LLM what tools are available    ║
# ╚══════════════════════════════════════════════════════════════╝

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the IT knowledge base for troubleshooting guides and how-to articles. Use when users ask about common IT issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword (e.g., 'vpn', 'password', 'email', 'printer', 'software')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_employee",
            "description": "Look up employee details by employee ID or name. Use when you need to verify identity or check employee status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Employee ID (e.g., 'E001') or name (e.g., 'Alice Johnson')"
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_system_status",
            "description": "Check the current status of IT systems (VPN, email, SSO, file server). Use when diagnosing if an issue is system-wide.",
            "parameters": {
                "type": "object",
                "properties": {
                    "system": {
                        "type": "string",
                        "enum": ["vpn_server", "email_server", "sso_portal", "file_server"],
                        "description": "System to check"
                    }
                },
                "required": ["system"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reset_password",
            "description": "Reset an employee's password and generate a temporary one. Use when employee requests a password reset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee ID (e.g., 'E001')"
                    }
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support ticket when the issue cannot be resolved immediately. Use as a last resort or for complex issues needing human IT staff.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short title for the ticket"},
                    "description": {"type": "string", "description": "Detailed description of the issue"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Ticket priority"
                    },
                    "employee_id": {"type": "string", "description": "Employee ID of the requester"}
                },
                "required": ["title", "description", "priority"]
            }
        }
    }
]


# ╔══════════════════════════════════════════════════════════════╗
# ║  TOOL IMPLEMENTATIONS — Functions the agent can call         ║
# ╚══════════════════════════════════════════════════════════════╝

def search_knowledge_base(query: str) -> str:
    """Search the IT knowledge base."""
    # TODO: Implement this function
    # 1. Search KNOWLEDGE_BASE dict for matching keys (case-insensitive)
    # 2. Return the matching article's title and content
    # 3. If no match found, return "No articles found for: {query}"
    #
    # Hint: Loop through KNOWLEDGE_BASE.items() and check if
    #       query.lower() is in the key
    pass


def lookup_employee(identifier: str) -> str:
    """Look up employee by ID or name."""
    # TODO: Implement this function
    # 1. Check if identifier matches an employee ID (e.g., "E001")
    # 2. If not, search by name (case-insensitive partial match)
    # 3. Return employee details as JSON string
    # 4. If not found, return "Employee not found: {identifier}"
    #
    # Hint: Use json.dumps() to format the output
    pass


def check_system_status(system: str) -> str:
    """Check system status."""
    # TODO: Implement this function
    # 1. Look up the system in SYSTEM_STATUS dict
    # 2. Return formatted status info
    # 3. If system not found, return "Unknown system: {system}"
    #
    # Hint: You can format as "System: {system} | Status: {status} | Load: {load}"
    pass


def reset_password(employee_id: str) -> str:
    """Reset employee password."""
    # TODO: Implement this function
    # 1. Verify the employee exists in EMPLOYEES
    # 2. Generate a temporary password (e.g., "TempPass_" + employee_id + "!2026")
    # 3. Return success message with the temp password
    # 4. If employee not found, return error message
    pass


def create_ticket(title: str, description: str, priority: str, employee_id: str = None) -> str:
    """Create a support ticket."""
    # TODO: Implement this function
    # 1. Create a ticket dict with: id, title, description, priority, employee_id, timestamp
    # 2. Append to TICKETS list
    # 3. Return confirmation with ticket ID
    #
    # Hint: ticket_id = f"TKT-{len(TICKETS) + 1001}"
    pass


# Map function names to implementations
TOOL_MAP = {
    "search_knowledge_base": search_knowledge_base,
    "lookup_employee": lookup_employee,
    "check_system_status": check_system_status,
    "reset_password": reset_password,
    "create_ticket": create_ticket,
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  AGENT LOOP — The core think → act → observe cycle          ║
# ╚══════════════════════════════════════════════════════════════╝

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
    """
    Run the single-agent loop.

    TODO: Implement the agent loop:
    1. Create messages list with system prompt + user message
    2. Loop up to max_turns:
       a. Call client.chat.completions.create() with model, messages, tools
       b. Get the assistant message
       c. Append it to messages
       d. If no tool_calls → return the message content (final answer)
       e. If tool_calls → execute each tool and append results to messages
    3. Return "Max turns reached" if loop exhausts

    Hint: Look at the code example in 04-agent-patterns.md
    """
    pass


# ╔══════════════════════════════════════════════════════════════╗
# ║  INTERACTIVE CLI                                             ║
# ╚══════════════════════════════════════════════════════════════╝

def main():
    """Interactive help desk CLI."""
    print("=" * 60)
    print("🤖 IT Help Desk Bot")
    print("=" * 60)
    print("Type your IT issue or question. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Thanks for using IT Help Desk. Goodbye!")
            break
        if not user_input:
            continue

        print("\n🤖 HelpBot: ", end="")
        response = run_agent(user_input)
        print(response)
        print()


# ╔══════════════════════════════════════════════════════════════╗
# ║  TEST QUERIES — Try these after implementing                 ║
# ╚══════════════════════════════════════════════════════════════╝

TEST_QUERIES = [
    "I can't connect to the VPN. My employee ID is E002.",
    "I need to reset my password. I'm Alice Johnson.",
    "Is the email server down? I can't send emails.",
    "How do I set up the printer on Floor 3?",
    "I need admin access to install Docker. Can you help? My ID is E001.",
]

def run_tests():
    """Run test queries to verify your implementation."""
    print("=" * 60)
    print("🧪 Running Test Queries")
    print("=" * 60)

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n--- Test {i} ---")
        print(f"User: {query}")
        response = run_agent(query)
        print(f"Bot:  {response}")
        print()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        main()
