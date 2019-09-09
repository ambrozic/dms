import json
import logging
import typing
from pathlib import Path

import sqlalchemy

from dms import settings
from dms.ds import Config
from dms.orm import Model
from dms.schema import Schema


class Loader:
    def __init__(self, source=None):
        self.source = source
        self._config = None
        self._storage = None
        self._models = None
        self._schemas = None
        self._tables = None

    @property
    def config(self):
        if self._config is None:
            self.source = self.source or json.load(open(settings.CONFIG))
            self._config = Config(**self.source)
        return self._config

    def models(self) -> typing.Dict[str, Model]:
        if self._models is None:
            logging.info("dms: loading models")
            self._models = {
                n: Model(name=n, meta=meta) for n, meta in self.config.models.items()
            }
        return self._models

    def model(self, name: str):
        return self.models()[name]

    def schemas(self) -> typing.Dict[str, Schema]:
        if self._schemas is None:
            logging.info("dms: loading schemas")
            self._schemas = {
                n: Schema(name=n, meta=meta) for n, meta in self.config.models.items()
            }
        return self._schemas

    def schema(self, name: str):
        return self.schemas()[name]

    def table(self, name: str):
        if self._tables is None:
            metadata = sqlalchemy.MetaData()
            metadata.reflect(sqlalchemy.create_engine(str(settings.DATABASE)))
            self._tables = {
                n: metadata.tables[meta.table] for n, meta in self.config.models.items()
            }
        return self._tables[name]

    def storage(self):
        if not self._storage:
            storage = Path(settings.STORAGE)
            if not storage.is_file():
                return
            with open(storage) as f:
                logging.info("dms: loading storage")
                self._storage = f.read()
        return self._storage


items = Loader()
