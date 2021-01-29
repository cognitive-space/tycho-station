import importlib
import json
import os

from pathlib import Path

import typer

app = typer.Typer()

GREEN = typer.colors.GREEN
DEFAULTS = {"backend": "s3", "outdir": "tycho_packages"}
DEFAULT_CONFIG = typer.Option(".tychoreg.json",
                              help="Config file path",
                              exists=False,
                              file_okay=True,
                              dir_okay=False,
                              writable=False,
                              readable=True,
                              resolve_path=True)


def get_env(key, data):
    if isinstance(data[key], dict):
        value = os.environ.get(data[key]["env"], data[key]["default"])
        data[key] = value


def get_backend(config):
    data = {}
    backend_kwargs = {}
    cli_kwargs = DEFAULTS

    if config.exists():
        with config.open() as fh:
            data = json.load(fh)

            if "tycho" in data:
                cli_kwargs = data["tycho"]
                for k, v in DEFAULTS.items():
                    if k not in cli_kwargs:
                        cli_kwargs[k] = v

    for key in cli_kwargs:
        get_env(key, cli_kwargs)

    if cli_kwargs["backend"] in data:
        backend_kwargs = data[cli_kwargs["backend"]]

    for key in backend_kwargs:
        get_env(key, backend_kwargs)

    mod = importlib.import_module('tychoreg.backends.{}'.format(
        cli_kwargs["backend"]))
    return mod.Backend(cli_kwargs, backend_kwargs)


@app.command()
def list(config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)

    for pkg in backend.list_packages():
        typer.echo(
            typer.style(pkg.name, fg=GREEN) +
            " -- Latest Version: {}".format(pkg.latest))


@app.command()
def list_versions(pkgname: str, config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    typer.echo(typer.style("{} Versions".format(pkgname), fg=GREEN))
    for version in backend.list_versions(pkgname):
        typer.echo("  - {}".format(version))


@app.command()
def push(pkgname: str, config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)


@app.command()
def pull(pkgname: str, force: bool = False, config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    backend.pull(pkgname, force)


if __name__ == "__main__":
    app()
