import os
from pathlib import Path


def resolve_target_path(working_directory: str, target: str) -> Path:
    """Resolve and validate that target path is within working directory."""
    working_dir = Path(working_directory).resolve()
    target_dir = (working_dir / target).resolve()

    try:
        target_dir.relative_to(working_dir)
    except ValueError as exc:
        raise PermissionError(
            f'"{target}" as it is outside the permitted working directory'
        ) from exc

    return target_dir


def get_files_info(working_directory: str, directory: str = ".") -> str:
    working_dir = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir, directory))

    valid_target_dir = os.path.commonpath([working_dir, target_dir]) == working_dir
    if not valid_target_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    files = ["Result for current directory:"]
    for file in os.listdir(target_dir):
        file_path = Path(os.path.join(target_dir, file))
        files.append(
            f"- {file}: file_size={file_path.stat().st_size}, is_dir={file_path.is_dir()}"
        )
    return "\n".join(files)


if __name__ == "__main__":
    print(get_files_info("playground_calculator"))
    print(get_files_info("playground_calculator", "../"))
