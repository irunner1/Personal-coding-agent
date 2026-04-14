from config import settings
from get_files_info import resolve_target_path

from google.genai import types


schema_get_file_contents = types.FunctionDeclaration(
    name="get_files_content",
    description="Return contents of the file up until max_file_contents_len characters",
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


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        target_file_path = resolve_target_path(working_directory, file_path)
    except PermissionError as e:
        return f"Error: Cannot read {e}"

    if not target_file_path.is_file():
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file_path, "r") as f:
            content = f.read(settings.MAX_FILE_CONTENTS_LENGTH)
            if f.read(1):
                content += (
                    f'[...File "{file_path}" truncated at '
                    f"{settings.MAX_FILE_CONTENTS_LENGTH} characters]"
                )
            return content
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    print(get_file_content("calculator", "main.py"))
    print(get_file_content("calculator", "lorem.txt"))
