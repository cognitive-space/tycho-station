import os
import json

from dataclasses import dataclass
from pathlib import Path

import typer


@dataclass
class Package:
    name: str

    @property
    def metapath(self):
        return Path(self.name) / "tycho.json"

    @property
    def latest(self):
        if hasattr(self, 'meta') and self.meta:
            return self.meta['latest']


class BackendBase:
    def __init__(self, cli_kwargs, backend_kwargs):
        self.outdir = Path(cli_kwargs['outdir'])
        self.config = backend_kwargs

    def list_packages(self):
        raise NotImplementedError

    def list_versions(self):
        raise NotImplementedError

    def read(self, path):
        raise NotImplementedError

    def json_data(self, path):
        return json.loads(self.read(path))

    def ensure_outdir(self):
        if not self.outdir.exists():
            os.makedirs(self.outdir)

    def write_etag(self, tag, path):
        path = str(path) + '.etag'
        self.message("File Hash: {}".format(tag))
        with open(path, 'w') as fh:
            fh.write(tag)

    def read_etag(self, path):
        epath = str(path) + '.etag'
        size = 0

        if os.path.exists(path):
            size = os.path.getsize(path)

        if os.path.exists(epath):
            with open(epath, 'r') as fh:
                return fh.read(), size

        return None, 0

    def message(self, msg):
        typer.echo(msg)

    def needs_update(self, remote_hash, remote_size, path):
        local_hash, local_size = self.read_etag(path)
        if local_hash:
            if local_hash == remote_hash and local_size == remote_size:
                return False

        return True
