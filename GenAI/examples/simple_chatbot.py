"""
Simple Chatbot Example
Demonstrates: Basic conversation flow, maintaining context, system prompts
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SimpleChatbot:
    """A simple chatbot that maintains conversation history"""
    
    def __init__(self, system_prompt=None):
        """
        Initialize chatbot with optional system prompt
        
        Args:
            system_prompt (str): Initial instructions for the AI
        """
        self.conversation_history = []
        
        # Set default system prompt if none provided
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """You are a helpful, friendly AI assistant. 
            You provide clear, concise answers and ask follow-up questions when appropriate."""
        
        # Add system message to history
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def chat(self, user_message):
        """
        Send a message and get response
        
        Args:
            user_message (str): The user's message
        
        Returns:
            str: The AI's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Make API call with full conversation history
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract assistant's response
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_history(self):
        """Return conversation history (excluding system prompt)"""
        return self.conversation_history[1:]  # Skip system message
    
    def clear_history(self):
        """Clear conversation history but keep system prompt"""
        self.conversation_history = [self.conversation_history[0]]
    
    def get_token_count_estimate(self):
        """Rough estimate of tokens used"""
        total_chars = sum(len(msg["content"]) for msg in self.conversation_history)
        return total_chars // 4  # Rough approximation

def main():
    """Interactive chatbot demo"""
    
    print("=" * 60)
    print("SIMPLE AI CHATBOT".center(60))
    print("=" * 60)
    print("\nCommands:")
    print("  'quit' or 'exit' - End conversation")
    print("  'history' - Show conversation history")
    print("  'clear' - Clear conversation history")
    print("  'tokens' - Show estimated token usage")
    print("\n" + "=" * 60 + "\n")
    
    # Create chatbot instance with custom system prompt
    bot = SimpleChatbot(
        system_prompt="""You are a knowledgeable coding tutor specializing in Python.
        Help users learn programming concepts with clear explanations and examples.
        Always encourage learning and provide step-by-step guidance."""
    )
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye! Happy coding! 👋")
            break
        
        if user_input.lower() == 'history':
            print("\n--- Conversation History ---")
            for msg in bot.get_history():
                role = msg["role"].capitalize()
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                print(f"{role}: {content}")
            print("----------------------------\n")
            continue
        
        if user_input.lower() == 'clear':
            bot.clear_history()
            print("\n[Conversation history cleared]\n")
            continue
        
        if user_input.lower() == 'tokens':
            token_estimate = bot.get_token_count_estimate()
            print(f"\n[Estimated tokens used: ~{token_estimate}]\n")
            continue
        
        # Get and display response
        response = bot.chat(user_input)
        print(f"\nAssistant: {response}\n")

if __name__ == "__main__":
    main()
