"""
subprocess_wrapper.py: Subprocess wrapper for error handling.
"""
import sys
import logging
import subprocess

from pathlib import Path


class SubprocessErrorLogging:
    """
    Display subprocess error output.
    """
    def __init__(self, process: subprocess.CompletedProcess) -> None:
        self.process = process


    def __str__(self) -> str:
        """
        Display subprocess error output in formatted string.

        Format:

        Command: <command>
        Return Code: <return code>
        Standard Output:
            <standard output line 1>
            <standard output line 2>
            ...
        Standard Error:
            <standard error line 1>
            <standard error line 2>
            ...
        """
        output = "Error: Subprocess failed.\n"
        output += f"    Command: {self.process.args}\n"
        output += f"    Return Code: {self.process.returncode}\n"
        output += f"    Standard Output:\n"
        output += self._format_output(self.process.stdout.decode("utf-8"))
        output += f"    Standard Error:\n"
        output += self._format_output(self.process.stderr.decode("utf-8"))
        output += f"\n    Called by: {self._get_caller()}\n"


        return output

    def _get_caller(self) -> str:
        """
        See which function called the subprocess.
        """
        _level = 2
        while True:
            frame = sys._getframe(_level)
            if frame is None:
                return "Unknown"
            if frame.f_code.co_filename != __file__:
                return f"{Path(frame.f_code.co_filename).name} -> {frame.f_code.co_name}() -> Line {frame.f_lineno}"
            _level += 1

            if _level > 10:
                break
        return "Unknown"


    def _format_output(self, output: str) -> str:
        """
        Format output.
        """
        if not output:
            return "        None\n"

        return "\n".join([f"        {line}" for line in output.split("\n") if line not in ["", "\n"]])


    def log(self) -> None:
        """
        Log subprocess error output.
        """
        logging.error(str(self))


class SubprocessWrapper:
    """
    Wrapper for subprocess.
    """
    def __init__(self, command: list, raise_on_error: bool = False) -> None:
        self.command = command
        self.raise_on_error = raise_on_error


    def run(self) -> bool:
        """
        Run subprocess command.
        """
        process = subprocess.run(self.command, capture_output=True)
        if process.returncode != 0:
            SubprocessErrorLogging(process).log()
            if self.raise_on_error:
                raise Exception("Subprocess failed.")
            return False

        return True