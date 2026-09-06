import importlib
import typer


app = typer.Typer()


@app.command()
def run(target: str):
    # Eg: uw run mart.actuarial.mortality_rate
    importlib.import_module(f"src.{target}").run()


def main():
    app()