# Personal coding agent

Python-based project for free coding agent using google genai (in purpose of testing google api)
Also there is ollama provider for usage with local models

## TODO

- check if i could make tunnel between pc with llm on gpu
- improve chat
- add `test` mode and tools for running
- ~~add full cli tool support/commands~~
- ~~add fully functional modes (agent, debug, architecture)~~
- ~~add memory for agent~~
- ~~add indexing for project~~
- ~~make requests not in single cli call, but in separate chat (like cursor cli)~~

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

Console script name is `coding_agent` (see `pyproject.toml`). Help and subcommands:

```bash
uv run coding_agent --help
# or from an activated venv where the package is installed:
coding_agent --help
```

Subcommands: `run` (single prompt), `chat` (REPL), `index` (file manifest JSON), `memory show|clear`. Global flags `--workdir`, `--provider`, and `--verbose` work on each subcommand (e.g. after `run`).

The default working directory is `./playground` (override with `--workdir`). Persistent notes live in `<workdir>/.coding_agent/memory.md`; the index is `<workdir>/.coding_agent/index.json`.

Example commands:

```bash
coding_agent "Read main.py" --verbose
coding_agent run "Plan a refactor on main.py" --mode plan
coding_agent run "Fix the failing test" --mode debug

# modes: general/agent, plan, arch/architecture, debug
coding_agent run "Your prompt" --provider gemini
coding_agent run "List files" --provider ollama --verbose --mode debug

coding_agent chat --mode agent --session mysession
coding_agent index --workdir ./playground
coding_agent memory show
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

```bash
(.venv) ➜  agent git:(main) ✗ coding_agent chat --session mysession
Chat mode. Commands: /exit, /quit, /clear. EOF to exit.

> how to run calculator app?
Calling function: get_files_info({'working_directory': './playground'})
Calling function: get_file_content({'file_path': 'calculator.py', 'working_directory': './playground'})
Calling function: run_python_file({'args': ['"3 + 5"'], 'file_path': 'calculator.py', 'working_directory': './playground'})
Calling function: run_python_file({'args': ['3', '+', '5'], 'file_path': 'calculator.py', 'working_directory': './playground'})
Response:
The calculator app runs correctly via the command line!

**To run it yourself, use the following format in your terminal:**

python calculator.py <number1> <operator> <number2> ...

**Example:** To calculate `10 * 2 - 1`:

python calculator.py 10 * 2 - 1

```

## Architecture

```architecture
┌──────────────────────┐ ┌───────────────────────────────────────────────────────────────────────────┐
│         CLI          │ │                                   Core                                    │
│                      │ │                                                                           │
│                      │ │                                                                           │
│ ┌──────────────────┐ │ │ ┌─────────────────────┐    ┌─────────────────┐   ┌──────────────────────┐ │
│ │                  │ │ │ │                     │    │                 │   │                      │ │
│ │  run subcommand  ├─┼►│ │ build_system_prompt ├───►│ Gemini / Ollama ├──►│ Tools + index search │ │
│ │                  │ │ │ │                     │    │                 │   │                      │ │
│ └──────────────────┘ │ │ └─────────────────────┘    └─────────────────┘   └──────────────────────┘ │
│                      │ │            ▲                                                              │
│ ┌──────────────────┐ │ │ ┌──────────┴──────────┐                                                   │
│ │                  │ │ │ │                     │                                                   │
│ │ chat subcommand  ├─┼►│ │   Message history   │                                                   │
│ │                  │ │ │ │                     │                                                   │
│ └──────────────────┘ │ │ └─────────────────────┘                                                   │
│                      │ │                                                                           │
│                      │ └───────────────────────────────────────────────────────────────────────────┘
│ ┌──────────────────┐ │ ┌────────────────────────┐
│ │                  │ │ │                        │
│ │ index subcommand ├─┼►│ Manifest index on disk │
│ │                  │ │ │                        │
│ └──────────────────┘ │ └────────────────────────┘
└──────────────────────┘
```
