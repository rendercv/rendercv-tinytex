import pathlib
import subprocess
import sys
from typing import Optional


def run_latex(
    latex_file_path: pathlib.Path, local_latex_command: Optional[str] = None
) -> pathlib.Path:
    """Run `pdftex` with the given $\\LaTeX$ file to render the PDF. If a local LaTeX
    command is provided, it will be called instead of `pdftex` of TinyTeX.

    Args:
        latex_file_path: The path to the $\\LaTeX$ file.
        local_latex_command: The local LaTeX command to use. If provided, it will be
            called instead of `pdftex` of TinyTeX.

    Returns:
        The path to the rendered PDF file.
    """
    # check if the file exists:
    if not latex_file_path.is_file():
        message = f"The file {latex_file_path} doesn't exist!"
        raise FileNotFoundError(message)

    if local_latex_command:
        executable = local_latex_command

        # check if the command is working:
        try:
            subprocess.run(
                [executable, "--version"],
                stdout=subprocess.DEVNULL,  # don't capture the output
                stderr=subprocess.DEVNULL,  # don't capture the error
                check=True,
            )
        except FileNotFoundError as e:
            message = (
                f"{executable} isn't installed! Please install LaTeX and try again (or"
                " don't use the [bright_black]--use-local-latex-command[/bright_black]"
                " option)."
            )
            raise FileNotFoundError(message) from e
    else:
        tinytex_binaries_directory = (
            pathlib.Path(__file__).parent / "tinytex-release" / "TinyTeX" / "bin"
        )

        executables = {
            "win32": tinytex_binaries_directory / "windows" / "pdflatex.exe",
            "linux": tinytex_binaries_directory / "x86_64-linux" / "pdflatex",
            "darwin": tinytex_binaries_directory / "universal-darwin" / "pdflatex",
        }

        if sys.platform not in executables:
            message = f"TinyTeX doesn't support the platform {sys.platform}!"
            raise OSError(message)

        executable = executables[sys.platform]

        # check if the executable exists:
        if not executable.is_file():
            message = (
                f"The TinyTeX executable ({executable}) doesn't exist! If you are"
                " cloning the repository, make sure to clone it recursively to get the"
                " TinyTeX binaries. See the developer guide for more information."
            )
            raise FileNotFoundError(message)

    # Before running LaTeX, make sure the PDF file is not open in another program,
    # that wouldn't allow LaTeX to write to it. Remove the PDF file if it exists,
    # if it's not removable, then raise an error:
    pdf_file_path = latex_file_path.with_suffix(".pdf")
    if pdf_file_path.is_file():
        try:
            pdf_file_path.unlink()
        except PermissionError as e:
            message = (
                f"The PDF file {pdf_file_path} is open in another program and doesn't"
                " allow RenderCV to rewrite it. Please close the PDF file."
            )
            raise RuntimeError(message) from e

    # Run LaTeX to render the PDF:
    command = [
        executable,
        str(latex_file_path.absolute()),
    ]
    with subprocess.Popen(
        command,
        cwd=latex_file_path.parent,
        stdout=subprocess.PIPE,  # capture the output
        stderr=subprocess.DEVNULL,  # don't capture the error
        stdin=subprocess.DEVNULL,  # don't allow LaTeX to ask for user input
    ) as latex_process:
        output = latex_process.communicate()  # wait for the process to finish
        if latex_process.returncode != 0:
            latex_file_path_log = latex_file_path.with_suffix(".log").read_text()

            if local_latex_command:
                message = (
                    f"The local LaTeX command {local_latex_command} couldn't render"
                    " this LaTeX file into a PDF. Check out the log file"
                    f" {latex_file_path.with_suffix('.log')} in the output directory"
                    " for more information. It is printed below:\n\n"
                )

                message = message + latex_file_path_log
                raise RuntimeError(message)

            message = (
                "Failed to render the PDF file. Check out the details in the log file:"
                f" {latex_file_path.with_suffix('.log')} \n\n"
                " It is also printed below:\n\n"
            )
            message = message + latex_file_path_log
            raise RuntimeError(message)

        try:
            output = output[0].decode("utf-8")
        except UnicodeDecodeError:
            output = output[0].decode("latin-1")

        if "Rerun to get" in output:
            # Run TinyTeX again to get the references right:
            subprocess.run(
                command,
                cwd=latex_file_path.parent,
                stdout=subprocess.DEVNULL,  # don't capture the output
                stderr=subprocess.DEVNULL,  # don't capture the error
                stdin=subprocess.DEVNULL,  # don't allow TinyTeX to ask for user input
                check=True,
            )

    return pdf_file_path
