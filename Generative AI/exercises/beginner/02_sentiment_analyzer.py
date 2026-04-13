"""
Exercise 2: Sentiment Analyzer
Difficulty: ⭐ Beginner
Time: 45 minutes

Task: Build a sentiment analyzer that classifies reviews and outputs JSON

Learning Goals:
- Practice classification tasks
- Work with structured output
- Handle JSON parsing
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

def analyze_sentiment(review):
    """
    Analyze sentiment of a review
    
    TODO: Implement this function to:
    1. Send review to AI for sentiment analysis
    2. Request JSON output with:
       - sentiment: positive/negative/neutral
       - confidence: 0.0-1.0
       - key_phrases: list of important words/phrases
    3. Parse and return the JSON
    
    Args:
        review (str): The review text
    
    Returns:
        dict: Sentiment analysis results
    """
    # YOUR CODE HERE
    # Hint: Use a clear prompt that requests JSON format
    # Hint: Consider using temperature=0.3 for consistent classification
    
    pass

def batch_analyze(reviews):
    """
    Analyze multiple reviews
    
    TODO: Implement batch analysis:
    1. Analyze each review
    2. Collect all results
    3. Calculate aggregate statistics
    
    Args:
        reviews (list): List of review strings
    
    Returns:
        list: List of analysis results
    """
    # YOUR CODE HERE
    pass

def display_results(results):
    """
    Display analysis results in a nice format
    
    TODO: Implement nice formatting:
    1. Show each review with its sentiment
    2. Display confidence scores
    3. Highlight key phrases
    """
    # YOUR CODE HERE
    pass

def main():
    """Main function"""
    print("="*60)
    print("SENTIMENT ANALYZER".center(60))
    print("="*60)
    
    # YOUR CODE HERE
    # 1. Analyze all test reviews
    # 2. Display results
    # 3. Show summary statistics (how many positive/negative/neutral)
    # 4. Allow user to enter their own review to analyze
    
    pass

if __name__ == "__main__":
    main()

# BONUS CHALLENGES:
# 1. Add emotion detection (happy, angry, sad, etc.)
# 2. Extract specific product aspects (quality, price, service)
# 3. Compare sentiment across different products
# 4. Generate a summary report in markdown format
