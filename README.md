# Personal coding agent

Python-based project for free coding agent using google genai (in testing google api purposes)
Also there is ollama provider for usage with local models

## Setup

```bash
uv sync
# or
pip install -r requirements.txt
```

## Usage

Show all functions:

```bash
python main.py --help
```

Project folder set to playground_calculator, so llm have access to all folder contents

Example commands:

```bash
python main.py "Read main.py" --verbose
python main.py "Plan a refactor on main.py" --mode plan
python main.py "Fix the failing test" --mode debug

# switch provider
python main.py "Your prompt" --provider gemini
python main.py "List files" --provider ollama --verbose --mode debug

```

### Example conversation

```bash
python main.py "Show current directory"

answer: 

python main.py "Plan a refactoring on main.py" --mode plan

answer:

```

## Architecture

Introduce a small provider interface used by main.py

```cmd
________________________________________________________
│                                                      |
│ ┌─────────┐   ┌──────────────┐   ┌──────────────┐    |
│ │         │   │              │   │              │    |
│ │ main.py ├──►│ LLMProvider  ├──►│ GeminiClient │    |
│ │         │   │       ┬      │   │              │    |
│ └────┬────┘   └──────────────┘   └──────────────┘    |
│      │                └────────┐                     |
│      │        ┌──────────────┐ │ ┌──────────────┐    |
│      │        │              │ │ │              │    |
│      └───────►│ ToolExecutor │◄┴►┤ OllamaClient │    |
│               │              │   │              │    |
│               └──────────────┘   └──────────────┘    |
--------------------------------------------------------
```
