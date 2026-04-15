# Personal coding agent

Python-based project for free coding agent using google genai (in purpose of testing google api)
Also there is ollama provider for usage with local models

## TODO:

- check if i could make tunnel between pc with llm on gpu
- add full cli tool support/commands
- add fully functional modes (agent, debug, architecture)
- add memory for agent
- add indexing for project
- make requests not in single cli call, but in separate chat (like cursor cli)

## Setup

If you plan to use cloud model, like gemini or cloud ollama models, setup `.env` file from `.env.example`
If you want to use it with local ollama model (i use `gemma4` for this), you should install ollama and local model with commands:

```bash
irm https://ollama.com/install.ps1 | iex # install ollama on windows (suppose you run local model on the high-end gpu)

ollama pull gemma4:latest # install gemma4 in ollama
```

Now you just need to instal dependencies:

```bash
uv sync
# or
pip install -r requirements.txt
```

### Tests

Run tests via command:

```bash
pytest
```

## Usage

Show all functions:

```bash
python -m src.main --help
# or with uv
uv run coding-agent --help 
# or inside venv
coding-agent --help
```

Project folder set to playground_calculator, so llm have access to all folder contents

Example commands:

```bash
coding-agent "Read main.py" --verbose
coding-agent "Plan a refactor on main.py" --mode plan
coding-agent "Fix the failing test" --mode debug

# switch provider
coding-agent "Your prompt" --provider gemini
coding-agent "List files" --provider ollama --verbose --mode debug

```

### Example conversation

```bash
(.venv) ➜  agent git:(main) ✗ coding-agent "Show current directory"

Calling function: get_files_info({})
Response:
The current directory contains the following items:
*   **lorem.txt**: A file with a size of 28 bytes.
*   **main.py**: A file with a size of 748 bytes.
*   **pkg**: A directory.
*   **tests.py**: A file with a size of 1380 bytes.
```

```bash
(.venv) ➜  agent git:(main) ✗ coding-agent "Plan a refactoring on main.py" --mode plan

Calling function: get_file_content({'file_path': 'main.py'})
Response:
This is a straightforward application launcher, and the existing code is quite functional. A refactoring plan should focus on improving **robustness**, **readability**, and **maintainability** by adding modern Python features like type hinting and better structure, without changing the core functionality.

Here is the refactoring plan for `main.py`.

### 📋 Refactoring Plan for `main.py`

#### 1. Add Docstrings and Type Hinting (Readability/Maintainability)
The most immediate improvement is to add a docstring to the `main` function explaining its purpose, arguments, and behavior. I will also add type hints to the `main` function signature.   

#### 2. Improve Argument Parsing Logic (Robustness)
The current logic for checking if arguments were passed is good, but I can make the logic clearer and handle the "empty/whitespace" case more explicitly right after extracting the expression.

#### 3. Error Handling (Robustness)
The broad `except Exception` is a catch-all. While sometimes necessary for simple CLI tools, it's better to at least ensure the error message is highly informative. I will keep the structure but ensure the error message is clean.
...
```

## Architecture

Introduce a small provider interface used by main.py

```schema
┌──────────────────────────────────────────────────────┐
│                                                      │
│ ┌─────────┐   ┌──────────────┐   ┌──────────────┐    │
│ │         │   │              │   │              │    │
│ │ main.py ├──►│ LLMProvider  ├──►│ GeminiClient │    │
│ │         │   │       ┬      │   │              │    │
│ └────┬────┘   └──────────────┘   └──────────────┘    │
│      │                └────────┐                     │
│      │        ┌──────────────┐ │ ┌──────────────┐    │
│      │        │              │ │ │              │    │
│      └───────►│ ToolExecutor │◄┴►┤ OllamaClient │    │
│               │              │   │              │    │
│               └──────────────┘   └──────────────┘    │
└──────────────────────────────────────────────────────┘ 
```
