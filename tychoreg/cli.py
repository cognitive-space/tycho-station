import importlib
import json
import os

from pathlib import Path
from typing import List

import typer
from dotenv import load_dotenv

app = typer.Typer()

GREEN = typer.colors.GREEN
DEFAULTS = {"backend": "s3", "outdir": "tycho_packages"}
OUTFILE = typer.Option(None,
                       help="Force output file path",
                       exists=False,
                       file_okay=True,
                       dir_okay=False,
                       writable=True,
                       readable=True,
                       resolve_path=True)
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

    if 'dotenv' in cli_kwargs:
        load_dotenv(dotenv_path=cli_kwargs['dotenv'])

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
def push(pkgname: str,
         version: str,
         file: Path,
         promote_latest: bool = False,
         config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    return backend.push(pkgname, version, file, promote_latest)


@app.command()
def promote(pkgname: str, version: str, config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    return backend.promote(pkgname, version)


@app.command()
def init(pkgname: str, filename: str, config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    return backend.init(pkgname, filename)


@app.command()
def pull(pkgname: str,
         version: str = 'latest',
         force: bool = False,
         outfile: Path = OUTFILE,
         config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    return backend.pull(pkgname, version, outfile, force)


@app.command()
def pull_list(pkgname: List[str],
              force: bool = False,
              config: Path = DEFAULT_CONFIG):
    backend = get_backend(config)
    for p in pkgname:
        backend.pull(p, 'latest', force=force)


if __name__ == "__main__":
    app()
