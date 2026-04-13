"""
Ticket Booking Agent — Single Agent Pattern
============================================
A single agent that helps users search events, check seat availability,
book tickets, cancel bookings, and look up booking details.

Pattern: SINGLE AGENT (tool-calling loop)

SETUP:
  pip install openai python-dotenv

  Create a .env file with:
    OPENAI_API_KEY=sk-...

RUN:
  python ticket_booking_agent.py
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ╔══════════════════════════════════════════════════════════════╗
# ║  MOCK DATABASE — Simulates the ticket-booking platform      ║
# ╚══════════════════════════════════════════════════════════════╝

EVENTS = {
    "EVT-101": {
        "name": "Avengers: Secret Wars",
        "type": "movie",
        "venue": "IMAX Cineplex, Downtown",
        "date": "2026-03-15",
        "showtimes": ["10:00 AM", "1:30 PM", "5:00 PM", "9:00 PM"],
        "price": {"standard": 12, "premium": 20, "vip": 35},
        "seats": {"standard": 42, "premium": 18, "vip": 6},
    },
    "EVT-102": {
        "name": "Taylor Swift — Eras Tour",
        "type": "concert",
        "venue": "National Stadium",
        "date": "2026-04-20",
        "showtimes": ["7:00 PM"],
        "price": {"general": 85, "floor": 150, "vip": 350},
        "seats": {"general": 5000, "floor": 200, "vip": 20},
    },
    "EVT-103": {
        "name": "Hamilton — The Musical",
        "type": "theatre",
        "venue": "Grand Theatre",
        "date": "2026-03-22",
        "showtimes": ["2:00 PM", "7:30 PM"],
        "price": {"balcony": 45, "orchestra": 95, "front_row": 175},
        "seats": {"balcony": 120, "orchestra": 60, "front_row": 10},
    },
    "EVT-104": {
        "name": "Lakers vs Warriors — NBA Playoffs",
        "type": "sports",
        "venue": "Crypto.com Arena",
        "date": "2026-04-05",
        "showtimes": ["8:00 PM"],
        "price": {"upper_deck": 60, "lower_bowl": 150, "courtside": 500},
        "seats": {"upper_deck": 3000, "lower_bowl": 500, "courtside": 12},
    },
    "EVT-105": {
        "name": "Dune: Part Three",
        "type": "movie",
        "venue": "Galaxy Cinemas, Uptown",
        "date": "2026-03-10",
        "showtimes": ["11:00 AM", "3:00 PM", "7:00 PM", "10:30 PM"],
        "price": {"standard": 14, "premium": 22, "imax": 28},
        "seats": {"standard": 80, "premium": 30, "imax": 15},
    },
}

USERS = {
    "U001": {"name": "Alice Johnson", "email": "alice@email.com", "wallet_balance": 500.00},
    "U002": {"name": "Bob Smith", "email": "bob@email.com", "wallet_balance": 200.00},
    "U003": {"name": "Carol Davis", "email": "carol@email.com", "wallet_balance": 1000.00},
}

BOOKINGS = []


# ╔══════════════════════════════════════════════════════════════╗
# ║  TOOL DEFINITIONS — Schema for OpenAI function calling      ║
# ╚══════════════════════════════════════════════════════════════╝

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": "Search for events by name, type (movie/concert/theatre/sports), or date. Returns matching events with basic info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword — event name, type (movie, concert, theatre, sports), or date (YYYY-MM-DD)"
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_event_details",
            "description": "Get full details of a specific event including showtimes, pricing tiers, and seat availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID (e.g. 'EVT-101')"
                    }
                },
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_seat_availability",
            "description": "Check how many seats are available for a specific event and seat tier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID (e.g. 'EVT-101')"
                    },
                    "tier": {
                        "type": "string",
                        "description": "Seat tier name (e.g. 'standard', 'premium', 'vip')"
                    },
                },
                "required": ["event_id", "tier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_tickets",
            "description": "Book tickets for an event. Deducts from user wallet and reduces available seats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (e.g. 'U001')"
                    },
                    "event_id": {
                        "type": "string",
                        "description": "Event ID (e.g. 'EVT-101')"
                    },
                    "tier": {
                        "type": "string",
                        "description": "Seat tier name"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of tickets to book"
                    },
                    "showtime": {
                        "type": "string",
                        "description": "Preferred showtime (e.g. '7:00 PM')"
                    },
                },
                "required": ["user_id", "event_id", "tier", "quantity", "showtime"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Cancel an existing booking by booking ID. Refunds the user's wallet and restores seats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {
                        "type": "string",
                        "description": "Booking ID (e.g. 'BKG-1001')"
                    }
                },
                "required": ["booking_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_bookings",
            "description": "Get all bookings for a specific user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (e.g. 'U001')"
                    }
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_wallet_balance",
            "description": "Check a user's wallet balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (e.g. 'U001')"
                    }
                },
                "required": ["user_id"],
            },
        },
    },
]


# ╔══════════════════════════════════════════════════════════════╗
# ║  TOOL IMPLEMENTATIONS                                       ║
# ╚══════════════════════════════════════════════════════════════╝

def search_events(query: str) -> str:
    """Search events by name, type, or date."""
    results = []
    q = query.lower()

    for eid, event in EVENTS.items():
        if (
            q in event["name"].lower()
            or q in event["type"].lower()
            or q in event["date"]
            or q in event["venue"].lower()
        ):
            tiers = ", ".join(
                f"{t} (${p})" for t, p in event["price"].items()
            )
            results.append(
                f"🎫 {eid} | {event['name']}\n"
                f"   Type: {event['type'].title()} | Date: {event['date']}\n"
                f"   Venue: {event['venue']}\n"
                f"   Tiers: {tiers}"
            )

    if results:
        return f"Found {len(results)} event(s):\n\n" + "\n\n".join(results)
    return f"No events found for '{query}'. Try searching by type (movie, concert, theatre, sports) or event name."


def get_event_details(event_id: str) -> str:
    """Get full details for one event."""
    eid = event_id.upper()
    if eid not in EVENTS:
        return f"Event not found: {event_id}. Available IDs: {', '.join(EVENTS.keys())}"

    e = EVENTS[eid]
    lines = [
        f"🎫  {e['name']}",
        f"Type      : {e['type'].title()}",
        f"Venue     : {e['venue']}",
        f"Date      : {e['date']}",
        f"Showtimes : {', '.join(e['showtimes'])}",
        "",
        "Pricing & Availability:",
    ]
    for tier in e["price"]:
        lines.append(
            f"  • {tier.replace('_', ' ').title():15s}  ${e['price'][tier]:>6}   "
            f"({e['seats'][tier]} seats left)"
        )
    return "\n".join(lines)


def check_seat_availability(event_id: str, tier: str) -> str:
    """Check seats for a specific event + tier."""
    eid = event_id.upper()
    t = tier.lower().replace(" ", "_")

    if eid not in EVENTS:
        return f"Event not found: {event_id}"
    if t not in EVENTS[eid]["seats"]:
        available = ", ".join(EVENTS[eid]["seats"].keys())
        return f"Tier '{tier}' not found for {eid}. Available tiers: {available}"

    seats = EVENTS[eid]["seats"][t]
    price = EVENTS[eid]["price"][t]
    return (
        f"Event: {EVENTS[eid]['name']}\n"
        f"Tier: {t.replace('_', ' ').title()}\n"
        f"Available seats: {seats}\n"
        f"Price per ticket: ${price}"
    )


def book_tickets(user_id: str, event_id: str, tier: str, quantity: int, showtime: str) -> str:
    """Book tickets — validates everything, deducts wallet, updates seats."""
    uid = user_id.upper()
    eid = event_id.upper()
    t = tier.lower().replace(" ", "_")

    # Validate user
    if uid not in USERS:
        return f"User not found: {user_id}. Available: {', '.join(USERS.keys())}"

    # Validate event
    if eid not in EVENTS:
        return f"Event not found: {event_id}. Available: {', '.join(EVENTS.keys())}"

    event = EVENTS[eid]

    # Validate tier
    if t not in event["price"]:
        available = ", ".join(event["price"].keys())
        return f"Tier '{tier}' not found. Available: {available}"

    # Validate showtime
    if showtime not in event["showtimes"]:
        return f"Showtime '{showtime}' not available. Options: {', '.join(event['showtimes'])}"

    # Validate seat count
    if quantity < 1:
        return "Quantity must be at least 1."
    if quantity > event["seats"][t]:
        return f"Not enough seats. Only {event['seats'][t]} {t} seats left."

    # Validate wallet
    total = event["price"][t] * quantity
    user = USERS[uid]
    if total > user["wallet_balance"]:
        return (
            f"Insufficient balance. Total: ${total:.2f}, "
            f"Wallet: ${user['wallet_balance']:.2f}. "
            f"Need ${total - user['wallet_balance']:.2f} more."
        )

    # ── All checks passed → make the booking ──
    user["wallet_balance"] -= total
    event["seats"][t] -= quantity

    booking_id = f"BKG-{1001 + len(BOOKINGS)}"
    booking = {
        "id": booking_id,
        "user_id": uid,
        "event_id": eid,
        "event_name": event["name"],
        "tier": t,
        "quantity": quantity,
        "showtime": showtime,
        "total_paid": total,
        "status": "confirmed",
        "booked_at": datetime.now().isoformat(),
    }
    BOOKINGS.append(booking)

    return (
        f"✅ Booking Confirmed!\n"
        f"  Booking ID : {booking_id}\n"
        f"  Event      : {event['name']}\n"
        f"  Date       : {event['date']}\n"
        f"  Showtime   : {showtime}\n"
        f"  Tier       : {t.replace('_', ' ').title()}\n"
        f"  Tickets    : {quantity}\n"
        f"  Total Paid : ${total:.2f}\n"
        f"  Remaining  : ${user['wallet_balance']:.2f}\n"
        f"\n  🎉 Enjoy the show!"
    )


def cancel_booking(booking_id: str) -> str:
    """Cancel a booking — refund wallet, restore seats."""
    bid = booking_id.upper()

    for booking in BOOKINGS:
        if booking["id"] == bid:
            if booking["status"] == "cancelled":
                return f"Booking {bid} is already cancelled."

            # Refund
            refund = booking["total_paid"]
            USERS[booking["user_id"]]["wallet_balance"] += refund
            EVENTS[booking["event_id"]]["seats"][booking["tier"]] += booking["quantity"]
            booking["status"] = "cancelled"

            return (
                f"✅ Booking {bid} cancelled successfully!\n"
                f"  Event   : {booking['event_name']}\n"
                f"  Tickets : {booking['quantity']} × {booking['tier'].replace('_', ' ').title()}\n"
                f"  Refund  : ${refund:.2f} → wallet\n"
                f"  New Balance: ${USERS[booking['user_id']]['wallet_balance']:.2f}"
            )

    return f"Booking not found: {booking_id}"


def get_user_bookings(user_id: str) -> str:
    """Return all bookings for a user."""
    uid = user_id.upper()
    if uid not in USERS:
        return f"User not found: {user_id}. Available: {', '.join(USERS.keys())}"

    user_bookings = [b for b in BOOKINGS if b["user_id"] == uid]
    if not user_bookings:
        return f"No bookings found for {USERS[uid]['name']} ({uid})."

    lines = [f"Bookings for {USERS[uid]['name']}:\n"]
    for b in user_bookings:
        status_icon = "✅" if b["status"] == "confirmed" else "❌"
        lines.append(
            f"  {status_icon} {b['id']} | {b['event_name']}\n"
            f"       {b['showtime']} | {b['quantity']}× {b['tier'].replace('_', ' ').title()} | "
            f"${b['total_paid']:.2f} | {b['status'].upper()}"
        )
    return "\n".join(lines)


def get_wallet_balance(user_id: str) -> str:
    """Check wallet balance."""
    uid = user_id.upper()
    if uid not in USERS:
        return f"User not found: {user_id}. Available: {', '.join(USERS.keys())}"

    user = USERS[uid]
    return f"💰 {user['name']}'s Wallet: ${user['wallet_balance']:.2f}"


# ── Tool dispatch map ─────────────────────────────────────────

TOOL_MAP = {
    "search_events": search_events,
    "get_event_details": get_event_details,
    "check_seat_availability": check_seat_availability,
    "book_tickets": book_tickets,
    "cancel_booking": cancel_booking,
    "get_user_bookings": get_user_bookings,
    "get_wallet_balance": get_wallet_balance,
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  AGENT LOOP — Think → Act → Observe                         ║
# ╚══════════════════════════════════════════════════════════════╝

SYSTEM_PROMPT = """You are TicketBot 🎫, a friendly and efficient ticket-booking assistant.

You help users:
  • Search for events (movies, concerts, theatre, sports)
  • View event details, pricing, and seat availability
  • Book tickets (deducting from their wallet)
  • Cancel bookings (with full refund)
  • Check their bookings and wallet balance

Available users for this demo:
  U001 — Alice Johnson ($500)
  U002 — Bob Smith ($200)
  U003 — Carol Davis ($1000)

Guidelines:
  1. When a user wants to book, always confirm the event, tier, showtime, and quantity BEFORE calling book_tickets.
  2. If the user hasn't told you their user ID, ask for it (or let them pick from the list above).
  3. Suggest cheaper tiers if the wallet balance is insufficient.
  4. After booking, summarise the confirmation clearly.
  5. Be warm, concise, and use emojis sparingly for a fun experience.
"""


def run_agent(user_input: str, conversation: list, max_turns: int = 8) -> str:
    """
    Run the single-agent tool-calling loop.
    
    The loop:
      1. Send messages to OpenAI (with tool definitions).
      2. If the model returns tool calls → execute them, append results, repeat.
      3. If the model returns plain text → that's the final answer.
    """
    conversation.append({"role": "user", "content": user_input})

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        conversation.append(msg.model_dump())

        # ── No tool calls → final answer ──
        if not msg.tool_calls:
            return msg.content

        # ── Execute each tool call ──
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            print(f"    🔧 Tool: {fn_name}({json.dumps(fn_args, ensure_ascii=False)})")
            result = TOOL_MAP[fn_name](**fn_args)
            print(f"    📋 Result preview: {result[:120]}...\n")

            conversation.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return "I've been going back and forth for a while — let me hand this off to a human agent."


# ╔══════════════════════════════════════════════════════════════╗
# ║  INTERACTIVE CLI                                             ║
# ╚══════════════════════════════════════════════════════════════╝

SAMPLE_QUERIES = [
    "What movies are playing this month?",
    "Show me details for the Taylor Swift concert",
    "I'm U001. Book 2 premium tickets for Avengers at 5:00 PM",
    "What are my bookings? I'm user U001",
    "Cancel booking BKG-1001",
    "I have $200 — what's the best event I can attend?",
]


def main():
    print("=" * 60)
    print("🎫  TicketBot — Single Agent Pattern Demo")
    print("=" * 60)
    print("\nSample queries you can try:")
    for i, q in enumerate(SAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print("\nType 'quit' to exit.\n")

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Thanks for using TicketBot. Enjoy your events!")
            break
        if not user_input:
            continue

        print()
        response = run_agent(user_input, conversation)
        print(f"🎫 TicketBot: {response}\n")


if __name__ == "__main__":
    main()
