from config import settings
from functions.get_files_info import resolve_target_path


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        target_file_path = resolve_target_path(working_directory, file_path)
    except PermissionError as e:
        return f"Error: Cannot read {e}"

    if not target_file_path.is_file():
        return f'Error: File not found or is not a regular file: "{file_path}"'

    limit = settings.MAX_FILE_CONTENTS_LENGTH
    try:
        with open(target_file_path, "r") as f:
            content = f.read(limit)
            if f.read(1):
                content += (
                    f'[...File "{file_path}" truncated at ' f"{limit} characters]"
                )
            return content
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    print(get_file_content("playground_calculator", "main.py"))
    print(get_file_content("playground_calculator", "lorem.txt"))
