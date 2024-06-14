import typer
from rich import print


class Error(typer.Exit):
    def __init__(self, message: str, kind: str = "ERROR"):
        super().__init__(code=1)
        print(f"[bold red]{kind}:[/bold red]", message)
