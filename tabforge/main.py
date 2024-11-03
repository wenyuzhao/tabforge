from pathlib import Path
import typer
from typing_extensions import Annotated
import rich

from . import render
from .error import Error


app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    context_settings=dict(help_option_names=["-h", "--help"]),
    pretty_exceptions_short=True,
    pretty_exceptions_show_locals=False,
)


@app.command()
def render_files(
    inputs: Annotated[
        list[Path],
        typer.Argument(
            ...,
            help="Input files or directories to render. File names must end with '.t.tex'.",
        ),
    ],
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Enable quiet mode.")
    ] = False,
    stdout: Annotated[
        bool, typer.Option(help="Capture stdout as part of the rendered result.")
    ] = False,
    builtins: Annotated[
        bool,
        typer.Option(
            help="Inject built-in functions into the rendering environment."
        ),
    ] = True,
):
    input_files: list[Path] = []
    # verify inputs
    for input in inputs:
        if not input.exists():
            raise Error(f"File not found: {input}")
        if input.is_file():
            if not input.suffix == ".tex":
                raise Error(f"Not a TeX file: {input}")
            if not input.name.endswith(".t.tex"):
                raise Error(f'Input file "{input}" does not end with ".t.tex".')
            input_files.append(input)
        elif input.is_dir():
            for file in input.glob("**/*.t.tex"):
                input_files.append(file)
    # render files
    for input in input_files:
        output = Path(str(input.name).replace(".t.tex", ".g.tex"))
        output_full_path = Path(str(input).replace(".t.tex", ".g.tex"))
        render.render_file(
            input=input,
            output=output,
            capture_stdout=stdout,
            inject_builtins=builtins,
        )
        if not quiet:
            rich.print(
                f"[bold green]RENDER[/bold green]",
                input,
                "[blue]➔[/blue]",
                output_full_path,
            )


def main():
    app()
