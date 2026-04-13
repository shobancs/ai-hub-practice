"""
Exercise 1: Temperature Explorer
Difficulty: ⭐ Beginner
Time: 30 minutes

Task: Create a program that generates responses with different temperatures
and lets users compare them.

Learning Goals:
- Understand temperature's effect
- Make multiple API calls
- Handle user input
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_with_temperature(prompt, temperature):
    """
    Generate a response with specified temperature
    
    TODO: Implement this function
    Args:
        prompt (str): The user's prompt
        temperature (float): Temperature value (0.0 to 2.0)
    
    Returns:
        str: The AI's response
    """
    # YOUR CODE HERE
    pass

def main():
    """
    Main function to run the temperature explorer
    
    TODO: Implement the main loop:
    1. Get a prompt from the user
    2. Generate 3 responses with temps: 0.0, 0.7, 1.5
    3. Display all responses
    4. Ask user which they prefer
    5. Option to try again or exit
    """
    print("="*60)
    print("TEMPERATURE EXPLORER".center(60))
    print("="*60)
    print("\nThis tool shows how temperature affects AI responses.")
    print("Low temp (0.0) = Focused, deterministic")
    print("Med temp (0.7) = Balanced")
    print("High temp (1.5) = Creative, varied\n")
    
    # YOUR CODE HERE
    # Hint: Use a while loop for repeated experiments
    # Hint: Store results in a list to display side-by-side
    
    pass

if __name__ == "__main__":
    main()

# BONUS CHALLENGES:
# 1. Let users choose their own temperature values
# 2. Save favorite responses to a file
# 3. Show word count for each response
# 4. Calculate cost estimate for the API calls
