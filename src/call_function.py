from google.genai import types

from config import settings
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.grep_project import grep_project
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from tools.tool_definitions import build_gemini_tool

available_functions = build_gemini_tool()

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
    "grep_project": grep_project,
}


def execute_tool(function_name: str, raw_args: dict | None) -> dict:
    """Run a tool by name; returns a JSON-serializable dict with `result` or `error`."""
    args = dict(raw_args) if raw_args else {}
    if function_name not in function_map:
        return {"error": f"Unknown function: {function_name}"}
    args["working_directory"] = settings.WORKING_DIR
    try:
        result = function_map[function_name](**args)
        return {"result": result}
    except TypeError as exc:
        return {"error": f"Invalid arguments for {function_name}: {exc}"}
    except Exception as exc:
        return {"error": str(exc)}


def gemini_tool_response(function_name: str, payload: dict) -> types.Content:
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response=payload,
            )
        ],
    )


def call_function(function_call, verbose: bool = False) -> types.Content:
    """Execute a Gemini function call object and return a tool Content part."""
    if verbose:
        print(f" - Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    function_name = function_call.name or ""
    payload = execute_tool(
        function_name,
        dict(function_call.args) if function_call.args else None,
    )
    return gemini_tool_response(function_name, payload)
