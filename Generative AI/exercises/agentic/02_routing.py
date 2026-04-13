"""
Exercise: Routing — Smart Email Classifier & Responder
=======================================================
Pattern: ROUTING (Chapter 2)

GOAL:
  Build a system that classifies incoming emails into categories
  and routes each to a specialised auto-responder.

YOUR TASKS:
  1. Implement the classify() function             (TODO 1)
  2. Add two more handler prompts                  (TODO 2)
  3. Implement confidence-based fallback routing    (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 02_routing.py
"""

import os, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(system: str, user: str) -> str:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return r.choices[0].message.content


# ═══════════════════════════════════════════════════════════
#  STEP 1: CLASSIFIER
# ═══════════════════════════════════════════════════════════

def classify(email: str) -> str:
    """
    TODO 1: Classify the email into ONE of these categories:
      - sales_inquiry
      - support_request
      - partnership
      - complaint
      - spam

    Call call_llm() with a system prompt that instructs the model to:
    - Read the email
    - Output ONLY the category name (no explanation)
    
    Return the category as a lowercase string.
    """
    # YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  STEP 2: SPECIALISED HANDLERS
# ═══════════════════════════════════════════════════════════

HANDLERS = {
    "sales_inquiry": (
        "You are a sales representative. Respond to the customer's inquiry "
        "about our product. Be enthusiastic, mention a free demo, and ask "
        "about their team size and timeline. Keep it under 100 words."
    ),
    "support_request": (
        "You are a technical support agent. Acknowledge the issue, ask for "
        "specifics (OS, browser, error message), and provide 2-3 initial "
        "troubleshooting steps. Keep it under 100 words."
    ),
    # ─────────────────────────────────────────────────────
    # TODO 2: Add handlers for "partnership" and "complaint"
    #
    # "partnership": (
    #     <write a system prompt for partnership inquiries>
    # ),
    # "complaint": (
    #     <write a system prompt for handling complaints>
    # ),
    # ─────────────────────────────────────────────────────
    "spam": None,  # No response for spam
}


def handle(category: str, email: str) -> str:
    """Route to the correct handler and generate a response."""
    if category == "spam":
        return "🗑️ [Spam detected — no response sent]"

    prompt = HANDLERS.get(category)
    if prompt is None:
        return f"⚠️ No handler for category: {category}"

    return call_llm(prompt, f"Customer email:\n{email}")


# ═══════════════════════════════════════════════════════════
#  BONUS: CONFIDENCE-BASED ROUTING
# ═══════════════════════════════════════════════════════════

def classify_with_confidence(email: str) -> tuple[str, float]:
    """
    TODO 3 (BONUS): Classify with a confidence score.
    
    Ask the LLM to return JSON like:
      {"category": "support_request", "confidence": 0.85}
    
    If confidence < 0.7, route to a "general" fallback handler.
    
    Return (category, confidence).
    """
    # YOUR CODE HERE
    category = classify(email)
    return (category, 1.0)  # Default: always confident


# ═══════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════

SAMPLE_EMAILS = [
    {
        "from": "john@bigcorp.com",
        "subject": "Interested in your AI platform",
        "body": "Hi, I'm the VP of Engineering at BigCorp. We're evaluating AI "
                "platforms for our team of 200 developers. Could you tell me about "
                "pricing and enterprise features? We'd like to start a pilot in Q2.",
    },
    {
        "from": "sarah@startup.io",
        "subject": "App crashes on login",
        "body": "Since the last update, the app crashes every time I try to log in. "
                "I'm on iOS 18 using an iPhone 15. I've tried reinstalling but the "
                "issue persists. This is blocking our entire team.",
    },
    {
        "from": "mike@partner.co",
        "subject": "Partnership opportunity",
        "body": "We're a developer tools company with 50K users. We'd love to explore "
                "an integration partnership where our users can access your AI features "
                "directly in our IDE. Would you be open to a call next week?",
    },
    {
        "from": "angry_customer@email.com",
        "subject": "WORST SERVICE EVER",
        "body": "I've been waiting 3 WEEKS for a response to my support ticket! "
                "This is completely unacceptable. I'm paying $500/month and can't "
                "even get basic support. I'm considering switching to a competitor.",
    },
    {
        "from": "deals@cheapmeds.xyz",
        "subject": "AMAZING OFFER — Act now!!!",
        "body": "Congratulations! You've been selected for an exclusive offer. "
                "Click here to claim your FREE prize. Limited time only!!!",
    },
]


def main():
    print("=" * 60)
    print("📧 Smart Email Classifier & Responder")
    print("=" * 60)

    for email in SAMPLE_EMAILS:
        print(f"\n{'─' * 60}")
        print(f"📩 From: {email['from']}")
        print(f"   Subject: {email['subject']}")

        full_email = f"From: {email['from']}\nSubject: {email['subject']}\n\n{email['body']}"

        category = classify(full_email)
        if category is None:
            print("   ❌ TODO 1 not implemented yet!")
            continue

        print(f"   🏷️  Category: {category.upper()}")

        response = handle(category, full_email)
        print(f"   💬 Response: {response}\n")


if __name__ == "__main__":
    main()
