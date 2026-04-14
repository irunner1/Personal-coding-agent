from functions.get_files_info import resolve_target_path


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
    print(
        write_file("playground_calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    )
    print(
        write_file(
            "playground_calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"
        )
    )
    print(
        write_file(
            "playground_calculator", "/tmp/temp.txt", "this should not be allowed"
        )
    )
