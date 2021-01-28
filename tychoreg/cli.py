import importlib
import json
import os

from pathlib import Path

import typer

app = typer.Typer()

GREEN = typer.colors.GREEN
DEFAULT_BACKEND = typer.Option("s3", help="Filesystem backend")
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


def get_backend(modname, config):
    mod = importlib.import_module('tychoreg.backends.{}'.format(modname))
    kwargs = {}
    if config.exists():
        with config.open() as fh:
            data = json.load(fh)
            if modname in data:
                kwargs = data[modname]

    for key in kwargs:
        get_env(key, kwargs)

    return mod.Backend(**kwargs)


@app.command()
def list(backend: str = DEFAULT_BACKEND, config: Path = DEFAULT_CONFIG):
    backend = get_backend(backend, config)

    for pkg in backend.list_packages():
        typer.echo(
            typer.style(pkg.name, fg=GREEN) +
            " -- Latest Version: {}".format(pkg.latest))


@app.command()
def list_versions(pkg: str,
                  backend: str = DEFAULT_BACKEND,
                  config: Path = DEFAULT_CONFIG):
    backend = get_backend(backend, config)
    typer.echo(typer.style("{} Versions".format(pkg), fg=GREEN))
    for version in backend.list_versions(pkg):
        typer.echo("  - {}".format(version))


@app.command()
def push(file_key: str,
         backend: str = DEFAULT_BACKEND,
         config: Path = DEFAULT_CONFIG):
    Backend = get_backend(backend, config)


@app.command()
def pull(file_key: str = None,
         force: bool = False,
         backend: str = DEFAULT_BACKEND,
         config: Path = DEFAULT_CONFIG):
    Backend = get_backend(backend, config)


if __name__ == "__main__":
    app()
