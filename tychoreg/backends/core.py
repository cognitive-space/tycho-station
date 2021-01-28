import json

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Package:
    name: str
    meta: dict = None

    @property
    def metapath(self):
        return Path(self.name) / "tycho.json"

    @property
    def latest(self):
        if self.meta:
            return self.meta['latest']


class BackendBase:
    def list_packages(self):
        raise NotImplementedError

    def list_versions(self):
        raise NotImplementedError

    def read(self, path):
        raise NotImplementedError

    def json_data(self, path):
        return json.loads(self.read(path))
