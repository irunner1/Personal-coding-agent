import shlex
import subprocess


def run_cli_command(
    command: str, check: bool = True, capture_output: bool = True, shell: bool = False
) -> str:
    """
    Runs a command-line interface (CLI) command.

    Args:
        command: The command string to execute.
        check: If True, raises a CalledProcessError if the command returns a non-zero exit code.
        capture_output: If True, stdout and stderr will be captured.
        shell: If True, the command will be executed through the shell (e.g., 'bash -c').
               Use with caution.

    Returns:
        Captured stdout/stderr when capture_output is True; otherwise an empty string on success.
        On failure with check=True, returns an error summary string instead of raising.
    """
    print(f"--- Running command: {command} ---")
    try:
        if shell:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=capture_output,
                text=True,
            )
        else:
            argv = shlex.split(command)
            result = subprocess.run(
                argv,
                check=check,
                capture_output=capture_output,
                text=True,
                shell=False,
            )
    except subprocess.CalledProcessError as e:
        return (
            f"ERROR: Command failed with exit code {e.returncode}\n"
            f"STDOUT: {e.stdout}\n"
            f"STDERR: {e.stderr}"
        )
    except FileNotFoundError:
        return (
            "ERROR: Command not found. Make sure the command is installed and in PATH."
        )
    except Exception as e:
        return f"An unexpected error occurred while running the command: {e}"

    print(f"Command finished (exit {result.returncode})")
    if capture_output:
        parts: list[str] = []
        if result.stdout:
            parts.append(result.stdout)
        if result.stderr:
            parts.append(result.stderr)
        return "".join(parts)
    return ""
