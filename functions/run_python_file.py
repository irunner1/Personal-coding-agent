import subprocess
from pathlib import Path
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run python file with arguements",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)


def run_python_file(working_directory: str, file_path: str, args=None) -> str:
    try:
        path = Path(working_directory).resolve()
        target = (path / file_path).resolve()

        if not target.is_relative_to(path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not target.is_file():
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target.suffix.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", str(target)]
        if args:
            command.extend(args)

        completed = subprocess.run(command, text=True, capture_output=True, timeout=30)

        result = ""
        if completed.returncode != 0:
            return "Process exited with code X"
        elif not completed.stderr and not completed.stdout:
            return "No output produced"
        else:
            result += f"STDOUT: {completed.stdout}"
            result += f"STDERR: {completed.stderr}"

        return result
    except Exception as e:
        return f"Error: executing Python file: {e}"


if __name__ == "__main__":
    print(run_python_file("calculator", "main.py"))
