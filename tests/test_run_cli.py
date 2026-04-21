import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.functions.run_cli_command import run_cli_command


@pytest.fixture(autouse=True)
def mock_subprocess_run():
    with patch(
        'subprocess.run',
        return_value=MagicMock(
            returncode=0, stdout="Mock STDOUT", stderr="Mock STDERR"
        ),
    ):
        yield


def test_run_cli_command_file_not_found_error_with_check_true():
    """Test that FileNotFoundError is properly handled when check=True"""
    with patch('subprocess.run') as mock_subprocess:
        mock_subprocess.side_effect = FileNotFoundError(
            "No such file or directory: 'non_existent_command'"
        )

        result = run_cli_command(
            command="non_existent_command", check=True, capture_output=True, shell=False
        )

        assert "ERROR: Command not found." in result
        assert "Make sure the command is installed and in PATH" in result


def test_run_cli_command_generic_exception_with_check_false():
    """Test that generic Exception returns error string when check=False"""
    with patch('subprocess.run') as mock_subprocess:
        mock_subprocess.side_effect = ValueError("Invalid command format")

        result = run_cli_command(
            command="invalid@@@command", check=False, capture_output=True, shell=False
        )

        assert "An unexpected error occurred while running the command:" in result
        assert "Invalid command format" in result


def test_run_cli_command_success_no_capture():
    command = "echo hello"
    with patch('subprocess.run') as mock_subprocess:
        mock_subprocess.return_value = MagicMock(
            returncode=0, stdout="Mock STDOUT", stderr="Mock STDERR"
        )

        run_cli_command(command=command, capture_output=False, check=False, shell=False)

        mock_subprocess.assert_called_with(
            command.split(), check=False, capture_output=False, text=True, shell=True
        )


def test_run_cli_command_check_raises_on_failure():
    error_output = "Command failed"

    with patch('subprocess.run') as mock_subprocess:
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="non_existent_command",
            output="Some output",
            stderr=error_output,
        )

        result = run_cli_command(
            command="non_existent_command",
            capture_output=True,
            check=True,
            shell=False,
        )

        assert "ERROR: Command failed with exit code 1" in result
        assert error_output in result


def test_run_cli_command_shell_invocation():
    command = "echo 'hi' && echo 'bye'"

    with patch('subprocess.run') as mock_subprocess:
        mock_subprocess.return_value = MagicMock(
            returncode=0, stdout="hi\\nbye", stderr=""
        )

        run_cli_command(command=command, capture_output=True, check=False, shell=True)

        mock_subprocess.assert_called_with(
            command, shell=True, check=False, capture_output=True, text=True
        )


def test_run_cli_command_with_arguments():
    command = "grep pattern file.txt"

    with patch('subprocess.run') as mock_subprocess:
        mock_subprocess.return_value = MagicMock(
            returncode=0, stdout="Match found", stderr=""
        )

        run_cli_command(command=command, capture_output=True, check=False, shell=False)

        mock_subprocess.assert_called_with(
            command.split(), check=False, capture_output=True, text=True, shell=True
        )
