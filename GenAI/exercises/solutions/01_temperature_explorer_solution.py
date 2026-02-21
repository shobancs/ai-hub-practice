"""
Exercise 1 SOLUTION: Temperature Explorer

This solution demonstrates:
- Making API calls with different temperatures
- Comparing responses side-by-side
- User interaction and input handling
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_with_temperature(prompt, temperature, model="gpt-3.5-turbo"):
    """Generate a response with specified temperature"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def display_comparison(prompt, responses):
    """Display responses in a formatted comparison"""
    print("\n" + "="*80)
    print(f"PROMPT: {prompt}")
    print("="*80)
    
    temps = [0.0, 0.7, 1.5]
    for temp, response in zip(temps, responses):
        print(f"\n📊 Temperature {temp}:")
        print("-" * 80)
        print(response)
        print(f"Word count: {len(response.split())} words")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    print("="*80)
    print("TEMPERATURE EXPLORER".center(80))
    print("="*80)
    print("\nExplore how temperature affects AI responses!")
    print("• Low temp (0.0) = Focused, consistent, factual")
    print("• Med temp (0.7) = Balanced creativity and coherence")
    print("• High temp (1.5) = Creative, varied, unpredictable\n")
    
    while True:
        # Get user prompt
        print("\n" + "-"*80)
        prompt = input("Enter your prompt (or 'quit' to exit): ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            print("\nThanks for exploring! Goodbye! 👋")
            break
        
        if not prompt:
            print("Please enter a prompt.")
            continue
        
        # Generate responses
        print("\nGenerating responses with different temperatures...")
        temperatures = [0.0, 0.7, 1.5]
        responses = []
        
        for temp in temperatures:
            print(f"  • Generating with temperature {temp}...", end="")
            response = generate_with_temperature(prompt, temp)
            responses.append(response)
            print(" ✓")
        
        # Display comparison
        display_comparison(prompt, responses)
        
        # Get user feedback
        print("\nWhich response do you prefer?")
        print("1. Temperature 0.0 (Focused)")
        print("2. Temperature 0.7 (Balanced)")
        print("3. Temperature 1.5 (Creative)")
        
        choice = input("Your choice (1-3): ").strip()
        
        if choice in ['1', '2', '3']:
            temp_map = {'1': 0.0, '2': 0.7, '3': 1.5}
            chosen_temp = temp_map[choice]
            print(f"\n✓ You preferred temperature {chosen_temp}!")
            
            # Ask if they want to save
            save = input("Save this response? (y/n): ").strip().lower()
            if save == 'y':
                filename = "favorite_responses.txt"
                with open(filename, 'a') as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Prompt: {prompt}\n")
                    f.write(f"Temperature: {chosen_temp}\n")
                    f.write(f"Response:\n{responses[int(choice)-1]}\n")
                print(f"✓ Saved to {filename}")
        
        # Continue or exit
        again = input("\nTry another prompt? (y/n): ").strip().lower()
        if again != 'y':
            print("\nThanks for exploring! Goodbye! 👋")
            break

if __name__ == "__main__":
    main()
