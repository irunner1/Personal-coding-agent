"""Single source of truth for tool names, descriptions, and JSON Schema parameters."""

from google.genai import types

TOOL_SPECS = [
    {
        "name": "get_files_info",
        "description": (
            "Lists files in a specified directory relative to the working directory, "
            "providing file size and whether each entry is a directory."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": (
                        "Directory path to list, relative to the working directory "
                        "(default: working directory root)."
                    ),
                },
            },
        },
    },
    {
        "name": "get_file_content",
        "description": (
            "Return file contents up to a configured maximum length; large files are truncated."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file relative to the working directory.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "run_python_file",
        "description": "Run a Python file under the working directory with optional CLI arguments.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the .py file relative to the working directory.",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of string arguments passed to the script.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write or overwrite a file relative to the working directory; "
            "creates parent directories as needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file relative to the working directory.",
                },
                "content": {
                    "type": "string",
                    "description": "Full text content to write.",
                },
            },
            "required": ["file_path", "content"],
        },
    },
]


def build_gemini_tool() -> types.Tool:
    declarations = [
        types.FunctionDeclaration(
            name=spec["name"],
            description=spec["description"],
            parameters_json_schema=spec["parameters"],
        )
        for spec in TOOL_SPECS
    ]
    return types.Tool(function_declarations=declarations)


def build_ollama_tools() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": spec["name"],
                "description": spec["description"],
                "parameters": spec["parameters"],
            },
        }
        for spec in TOOL_SPECS
    ]
