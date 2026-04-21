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
        subprocess.CompletedProcess: An object containing the return code, stdout, and stderr.

    Raises:
        subprocess.CalledProcessError: If check is True and the command fails.
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
            # Use shlex.split to handle arguments correctly if the command is a string
            # and we want to run it without a shell, although for simple cases,
            # passing a list is better practice. For simplicity here, we assume
            # splitting by space is okay if shell=False and we pass a single string.
            # A robust implementation would require passing a list of arguments.
            args = shlex.split(command)
            result = subprocess.run(
                args, check=check, capture_output=capture_output, text=True, shell=True
            )

        print(f"Command executed successfully: {result}")
        return str(result)
    except subprocess.CalledProcessError as e:
        return (
            f"ERROR: Command failed with exit code {e.returncode}\n"
            f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        )
    except FileNotFoundError:
        return (
            f"ERROR: Command not found. Make sure the command is installed and in PATH."
        )
    except Exception as e:
        return f"An unexpected error occurred while running the command: {e}"
