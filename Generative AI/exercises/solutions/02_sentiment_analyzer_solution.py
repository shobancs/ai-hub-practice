"""
Exercise 2 SOLUTION: Sentiment Analyzer

This solution demonstrates:
- Classification with LLMs
- Structured JSON output
- JSON parsing and error handling
- Batch processing
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test data
TEST_REVIEWS = [
    "This product is amazing! Best purchase ever.",
    "Terrible quality. Broke after one day.",
    "It's okay, nothing special.",
    "Great value for money, highly recommend!",
    "Worst customer service. Never buying again.",
    "Decent product, works as described."
]

def analyze_sentiment(review, model="gpt-3.5-turbo"):
    """Analyze sentiment of a review and return JSON"""
    
    prompt = f"""Analyze the sentiment of this review and return a JSON object.

Review: "{review}"

Return JSON with exactly these fields:
- sentiment: "positive", "negative", or "neutral"
- confidence: float from 0.0 to 1.0
- key_phrases: list of 2-3 important phrases from the review

JSON:"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis expert. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3  # Lower temp for consistent classification
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON if wrapped in markdown
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        result = json.loads(result_text)
        
        # Add the original review
        result['review'] = review
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON: {e}")
        return {
            'review': review,
            'sentiment': 'error',
            'confidence': 0.0,
            'key_phrases': [],
            'error': str(e)
        }
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return {
            'review': review,
            'sentiment': 'error',
            'confidence': 0.0,
            'key_phrases': [],
            'error': str(e)
        }

def batch_analyze(reviews):
    """Analyze multiple reviews"""
    results = []
    
    print(f"\nAnalyzing {len(reviews)} reviews...")
    for i, review in enumerate(reviews, 1):
        print(f"  [{i}/{len(reviews)}] Analyzing...", end="")
        result = analyze_sentiment(review)
        results.append(result)
        print(" ✓")
    
    return results

def calculate_statistics(results):
    """Calculate aggregate statistics"""
    sentiments = [r['sentiment'] for r in results if r['sentiment'] != 'error']
    
    stats = {
        'total': len(results),
        'positive': sentiments.count('positive'),
        'negative': sentiments.count('negative'),
        'neutral': sentiments.count('neutral'),
        'errors': sum(1 for r in results if r['sentiment'] == 'error')
    }
    
    # Calculate percentages
    if stats['total'] > 0:
        for key in ['positive', 'negative', 'neutral']:
            stats[f'{key}_percent'] = (stats[key] / stats['total']) * 100
    
    return stats

def display_results(results, show_details=True):
    """Display analysis results"""
    
    # Color codes for terminal
    COLORS = {
        'positive': '\033[92m',  # Green
        'negative': '\033[91m',  # Red
        'neutral': '\033[93m',   # Yellow
        'reset': '\033[0m'
    }
    
    print("\n" + "="*80)
    print("SENTIMENT ANALYSIS RESULTS".center(80))
    print("="*80)
    
    for i, result in enumerate(results, 1):
        sentiment = result['sentiment']
        confidence = result.get('confidence', 0)
        
        # Color code based on sentiment
        color = COLORS.get(sentiment, COLORS['reset'])
        
        print(f"\n{i}. Review: \"{result['review']}\"")
        print(f"   Sentiment: {color}{sentiment.upper()}{COLORS['reset']} "
              f"(Confidence: {confidence:.2f})")
        
        if show_details and result.get('key_phrases'):
            print(f"   Key phrases: {', '.join(result['key_phrases'])}")
    
    # Display statistics
    stats = calculate_statistics(results)
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS".center(80))
    print("="*80)
    print(f"\nTotal reviews: {stats['total']}")
    print(f"  ✓ Positive: {stats['positive']} ({stats.get('positive_percent', 0):.1f}%)")
    print(f"  ✗ Negative: {stats['negative']} ({stats.get('negative_percent', 0):.1f}%)")
    print(f"  ○ Neutral:  {stats['neutral']} ({stats.get('neutral_percent', 0):.1f}%)")
    
    if stats['errors'] > 0:
        print(f"  ⚠ Errors:   {stats['errors']}")

def main():
    """Main function"""
    print("="*80)
    print("SENTIMENT ANALYZER".center(80))
    print("="*80)
    print("\nAnalyzes product reviews and classifies sentiment.\n")
    
    # Analyze test reviews
    print("Analyzing test reviews...")
    results = batch_analyze(TEST_REVIEWS)
    display_results(results)
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("\nEnter your own reviews to analyze (or 'quit' to exit)")
    
    while True:
        print("\n" + "-"*80)
        review = input("Enter a review: ").strip()
        
        if review.lower() in ['quit', 'exit', 'q']:
            break
        
        if not review:
            print("Please enter a review.")
            continue
        
        print("Analyzing...")
        result = analyze_sentiment(review)
        display_results([result], show_details=True)
        
        # Ask to continue
        again = input("\nAnalyze another? (y/n): ").strip().lower()
        if again != 'y':
            break
    
    print("\nThank you for using Sentiment Analyzer! 👋")

if __name__ == "__main__":
    main()
