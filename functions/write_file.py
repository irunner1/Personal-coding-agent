from get_files_info import resolve_target_path
from google.genai import types


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write content to file on file_path in working_directory, if no file, create file on working directory",
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


def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        target_file_path = resolve_target_path(working_directory, file_path)
    except PermissionError as e:
        return f"Error: Cannot write to {e}"

    if target_file_path.is_dir():
        return f'Error: Cannot write to "{file_path}" as it is a directory'

    target_file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(target_file_path, "w") as f:
            f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f"Error: Failed to write file - {e}"


if __name__ == "__main__":
    print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
    print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
    print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
