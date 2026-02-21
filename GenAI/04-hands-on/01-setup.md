# Setting Up Your Development Environment

## Overview

This guide will help you set up everything needed to work with Generative AI and follow along with the course examples.

---

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Internet**: Stable connection for API calls

### Basic Knowledge
- Basic programming experience (Python preferred)
- Command line/terminal basics
- Text editor familiarity

---

## Step 1: Install Python

### Check if Python is Installed
```bash
python --version
# or
python3 --version
```

Should show Python 3.8 or higher.

### Install Python (if needed)

**macOS**:
```bash
# Using Homebrew
brew install python3
```

**Windows**:
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ☑️ Check "Add Python to PATH"
4. Click Install

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Verify Installation**:
```bash
python3 --version
pip3 --version
```

---

## Step 2: Set Up Project Directory

### Create Project Folder
```bash
# Navigate to your preferred location
cd ~/Desktop/Training

# Create and enter project directory
mkdir GenAI-Practice
cd GenAI-Practice
```

### Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Create Project Structure
```bash
# Create directories
mkdir src notebooks data examples tests

# Create files
touch .env .gitignore README.md
```

**Result**:
```
GenAI-Practice/
├── venv/
├── src/
├── notebooks/
├── data/
├── examples/
├── tests/
├── .env
├── .gitignore
└── README.md
```

---

## Step 3: Install Required Packages

### Download Requirements File

Create `requirements.txt`:
```bash
cat > requirements.txt << 'EOF'
# Core AI Libraries
openai>=1.12.0
anthropic>=0.18.0

# LangChain
langchain>=0.1.0
langchain-openai>=0.0.5

# Vector Database
chromadb>=0.4.22

# Data Processing
numpy>=1.24.0
pandas>=2.0.0

# Web & APIs
requests>=2.31.0
beautifulsoup4>=4.12.0
fastapi>=0.109.0
uvicorn>=0.27.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.66.0
tenacity>=8.2.0

# Jupyter
jupyter>=1.0.0
ipykernel>=6.29.0
ipywidgets>=8.1.0

# Visualization
matplotlib>=3.8.0
plotly>=5.18.0

# Testing
pytest>=8.0.0
EOF
```

### Install Packages
```bash
pip install -r requirements.txt
```

This may take 5-10 minutes.

### Verify Installation
```bash
python -c "import openai; print('OpenAI:', openai.__version__)"
python -c "import langchain; print('LangChain:', langchain.__version__)"
python -c "import chromadb; print('ChromaDB:', chromadb.__version__)"
```

---

## Step 4: Get API Keys

### OpenAI API Key

1. **Sign up**: Go to [platform.openai.com](https://platform.openai.com)
2. **Create account** or log in
3. **Add payment method**: Go to Billing → Add payment method
4. **Generate API key**: 
   - Click on your profile → "View API keys"
   - Click "Create new secret key"
   - Copy the key (you won't see it again!)

**Pricing** (as of 2026):
- GPT-3.5-Turbo: ~$0.50 per 1M tokens
- GPT-4: ~$30 per 1M tokens (input)
- Embeddings: ~$0.13 per 1M tokens

**Cost Control**:
- Set usage limits in your OpenAI account
- Start with GPT-3.5-turbo for testing
- Monitor usage regularly

### Anthropic API Key (Optional)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up/log in
3. Generate API key from dashboard

### Store API Keys Securely

**Create `.env` file**:
```bash
# In your project root
cat > .env << 'EOF'
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Other services (add as needed)
EOF
```

**⚠️ Important**: Never commit `.env` to version control!

**Update `.gitignore`**:
```bash
cat > .gitignore << 'EOF'
# Environment
venv/
.env
*.env

# Python
__pycache__/
*.py[cod]
*.so
.Python

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Data
data/raw/
*.csv
*.json
*.db

# Secrets
*.key
*.pem
EOF
```

---

## Step 5: Test Your Setup

### Create Test Script

**`test_setup.py`**:
```python
"""
Test script to verify environment setup
"""

import sys
import os
from dotenv import load_dotenv

def test_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    return True

def test_imports():
    """Test key package imports"""
    packages = [
        'openai',
        'anthropic',
        'langchain',
        'chromadb',
        'numpy',
        'pandas',
        'requests',
        'dotenv'
    ]
    
    print("\nTesting package imports...")
    success = True
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} - not installed")
            success = False
    
    return success

def test_api_keys():
    """Check API key configuration"""
    load_dotenv()
    
    print("\nChecking API keys...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        print("  ✓ OpenAI API key found")
    else:
        print("  ❌ OpenAI API key not found or invalid")
        return False
    
    return True

def test_api_connection():
    """Test API connectivity"""
    from openai import OpenAI
    
    print("\nTesting API connection...")
    
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("  ✓ API connection successful")
            print(f"  Response: {response.choices[0].message.content}")
            return True
    except Exception as e:
        print(f"  ❌ API test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING GENERATIVE AI ENVIRONMENT SETUP")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports),
        ("API Keys", test_api_keys),
        ("API Connection", test_api_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED - You're ready to go!")
    else:
        print("❌ Some tests failed - please fix issues above")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

### Run Test
```bash
python test_setup.py
```

**Expected Output**:
```
============================================================
TESTING GENERATIVE AI ENVIRONMENT SETUP
============================================================
✓ Python 3.11.7

Testing package imports...
  ✓ openai
  ✓ anthropic
  ✓ langchain
  ✓ chromadb
  ✓ numpy
  ✓ pandas
  ✓ requests
  ✓ dotenv

Checking API keys...
  ✓ OpenAI API key found

Testing API connection...
  ✓ API connection successful
  Response: test successful

============================================================
✅ ALL TESTS PASSED - You're ready to go!
============================================================
```

---

## Step 6: Set Up Jupyter Notebooks

### Install Jupyter Kernel
```bash
# Install kernel for this environment
python -m ipykernel install --user --name=genai --display-name="GenAI Python"
```

### Launch Jupyter
```bash
jupyter notebook
```

This opens in your browser at `http://localhost:8888`

### Test Notebook

Create new notebook → Select "GenAI Python" kernel

**Test cell**:
```python
import openai
from dotenv import load_dotenv
import os

load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, testing from Jupyter!"}]
)

print(response.choices[0].message.content)
```

---

## Step 7: Install Code Editor (Optional but Recommended)

### VS Code (Recommended)

1. Download from [code.visualstudio.com](https://code.visualstudio.com)
2. Install
3. Install extensions:
   - Python (Microsoft)
   - Jupyter (Microsoft)
   - Python Indent
   - autoDocstring

### Configure VS Code

**Select Python Interpreter**:
1. Open VS Code
2. Open your project folder
3. Press `Cmd/Ctrl + Shift + P`
4. Type "Python: Select Interpreter"
5. Choose the one in your `venv` folder

**Test**:
Create `hello.py`:
```python
print("Hello from VS Code!")
```

Run with `F5` or right-click → "Run Python File"

---

## Step 8: Alternative APIs (Optional)

### Anthropic (Claude)

```bash
pip install anthropic
```

**Test**:
```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(message.content[0].text)
```

### Local Models (Ollama)

For running models locally without API costs:

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Or download from ollama.com for Windows

# Pull a model
ollama pull llama3.2

# Run model
ollama run llama3.2
```

**Use in Python**:
```bash
pip install ollama
```

```python
import ollama

response = ollama.chat(model='llama3.2', messages=[
    {'role': 'user', 'content': 'Why is the sky blue?'}
])

print(response['message']['content'])
```

---

## Common Issues & Solutions

### Issue: `pip: command not found`
```bash
# Try pip3 instead
pip3 install -r requirements.txt

# Or use python -m pip
python3 -m pip install -r requirements.txt
```

### Issue: Virtual environment not activating
```bash
# Make sure you're in the project directory
cd /path/to/GenAI-Practice

# Check if venv folder exists
ls -la venv/

# Re-create if needed
python3 -m venv venv --clear
```

### Issue: API key not found
```bash
# Verify .env file exists
cat .env

# Check it's in the same directory as your script
ls -la

# Load explicitly in Python
from dotenv import load_dotenv
load_dotenv()  # This should be at the top of your script
```

### Issue: Import errors
```bash
# Make sure virtual environment is activated
which python  # Should show path to venv

# Reinstall problematic package
pip install --upgrade --force-reinstall openai
```

### Issue: Jupyter can't find packages
```bash
# Reinstall kernel
python -m ipykernel install --user --name=genai --display-name="GenAI Python" --force

# Restart Jupyter
```

---

## Quick Reference Commands

### Virtual Environment
```bash
# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Deactivate
deactivate

# Verify active
which python
```

### Package Management
```bash
# Install package
pip install package-name

# Install from requirements
pip install -r requirements.txt

# List installed
pip list

# Upgrade package
pip install --upgrade package-name

# Freeze current packages
pip freeze > requirements.txt
```

### Jupyter
```bash
# Launch
jupyter notebook

# Launch in specific directory
jupyter notebook /path/to/notebooks

# List kernels
jupyter kernelspec list

# Remove kernel
jupyter kernelspec remove genai
```

---

## Next Steps

Now that your environment is set up:

1. ✅ Run the example code from the course
2. ✅ Open the Jupyter notebooks in `/notebooks`
3. ✅ Try the exercises in `/examples`
4. ✅ Start building your own AI applications!

---

## Additional Resources

### Documentation
- [OpenAI API Docs](https://platform.openai.com/docs)
- [LangChain Docs](https://python.langchain.com)
- [ChromaDB Docs](https://docs.trychroma.com)

### Learning
- [Python Tutorial](https://docs.python.org/3/tutorial/)
- [Jupyter Tutorial](https://jupyter.org/try)

### Community
- [OpenAI Forum](https://community.openai.com)
- [LangChain Discord](https://discord.gg/langchain)

---

**Congratulations! Your environment is ready.** 🎉

**Next**: [Building Your First AI Application](./02-first-app.md)
