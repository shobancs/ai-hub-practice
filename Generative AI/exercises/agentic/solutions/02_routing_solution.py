"""
Solution: Routing — Smart Email Classifier & Responder
=======================================================
Pattern: ROUTING (Chapter 2)

Complete solution with all TODOs implemented.
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
#  STEP 1: CLASSIFIER  ✅ (TODO 1)
# ═══════════════════════════════════════════════════════════

def classify(email: str) -> str:
    """Classify the email into a category."""
    result = call_llm(
        "You are an email classifier. Classify the email into exactly ONE "
        "of these categories:\n"
        "- sales_inquiry (someone interested in buying or learning about products)\n"
        "- support_request (someone with a technical issue or bug)\n"
        "- partnership (someone proposing a collaboration or integration)\n"
        "- complaint (someone unhappy about service or experience)\n"
        "- spam (unsolicited, promotional, or scam email)\n\n"
        "Output ONLY the category name in lowercase. Nothing else.",
        f"Email:\n{email}",
    )
    return result.strip().lower()


# ═══════════════════════════════════════════════════════════
#  STEP 2: SPECIALISED HANDLERS  ✅ (TODO 2)
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
    "partnership": (
        "You are a partnerships manager. Express genuine interest in the "
        "collaboration opportunity. Ask about their user base, integration "
        "timeline, and preferred partnership model (API, white-label, referral). "
        "Suggest scheduling a discovery call. Keep it under 100 words."
    ),
    "complaint": (
        "You are a customer success manager. Sincerely apologise for the poor "
        "experience. Acknowledge the specific issue. Offer a concrete next step "
        "(escalation to senior support, account credit, or direct call). "
        "Be empathetic, not defensive. Keep it under 100 words."
    ),
    "spam": None,
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
#  BONUS: CONFIDENCE-BASED ROUTING  ✅ (TODO 3)
# ═══════════════════════════════════════════════════════════

def classify_with_confidence(email: str) -> tuple[str, float]:
    """Classify with a confidence score."""
    result = call_llm(
        "You are an email classifier. Classify the email into exactly ONE "
        "of these categories:\n"
        "- sales_inquiry\n"
        "- support_request\n"
        "- partnership\n"
        "- complaint\n"
        "- spam\n\n"
        "Also estimate your confidence (0.0 to 1.0).\n\n"
        "Respond ONLY in this JSON format, nothing else:\n"
        '{"category": "...", "confidence": 0.85}',
        f"Email:\n{email}",
    )
    try:
        data = json.loads(result.strip())
        category = data["category"].strip().lower()
        confidence = float(data["confidence"])
        return (category, confidence)
    except (json.JSONDecodeError, KeyError, ValueError):
        # Fall back to basic classification
        category = classify(email)
        return (category, 0.5)


GENERAL_HANDLER = (
    "You are a helpful customer service agent. The email didn't clearly fit "
    "one department. Write a polite, general response acknowledging the email "
    "and asking clarifying questions to route it properly. Keep it under 100 words."
)


def handle_with_confidence(email: str) -> tuple[str, str, float]:
    """Classify with confidence, fallback to general if low confidence."""
    category, confidence = classify_with_confidence(email)
    print(f"   🎯 Confidence: {confidence:.0%}")

    if confidence < 0.7:
        category = "general"
        response = call_llm(GENERAL_HANDLER, f"Customer email:\n{email}")
    else:
        response = handle(category, email)

    return category, response, confidence


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

        category, response, confidence = handle_with_confidence(full_email)
        print(f"   🏷️  Category: {category.upper()}")
        print(f"   💬 Response: {response}\n")


if __name__ == "__main__":
    main()
