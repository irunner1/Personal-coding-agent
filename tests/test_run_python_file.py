from pathlib import Path

from functions.run_python_file import run_python_file


def test_run_main_no_args(playground_dir: Path) -> None:
    result = run_python_file(str(playground_dir), "main.py")
    assert result == (
        "STDOUT: Calculator App\n"
        'Usage: python main.py "<expression>"\n'
        'Example: python main.py "3 + 5"\n'
        "STDERR: "
    )


def test_run_main_with_expression(playground_dir: Path) -> None:
    result = run_python_file(str(playground_dir), "main.py", ["3 + 5"])
    assert result == (
        "STDOUT: {\n" '  "expression": "3 + 5",\n' '  "result": 8\n' "}\n" "STDERR: "
    )


def test_run_unit_tests(playground_dir: Path) -> None:
    result = run_python_file(str(playground_dir), "tests.py")
    assert "Ran 9 tests" in result
    assert "OK" in result


def test_rejects_path_outside_workdir(playground_dir: Path) -> None:
    file_path = "../main.py"
    result = run_python_file(str(playground_dir), file_path)
    assert result == (
        f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    )


def test_missing_file(playground_dir: Path) -> None:
    filename = "nonexistent.p"
    result = run_python_file(str(playground_dir), filename)
    assert result == f'Error: "{filename}" does not exist or is not a regular file'


def test_rejects_non_python_file(playground_dir: Path) -> None:
    file_path = "lorem.txt"
    result = run_python_file(str(playground_dir), file_path)
    assert result == f'Error: "{file_path}" is not a Python file'
