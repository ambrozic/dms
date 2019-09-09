import typing
import uuid
from datetime import date, datetime

import sqlalchemy
from sqlalchemy import asc, desc
from sqlalchemy.engine import RowProxy
from sqlalchemy.sql import ClauseElement

from dms import db, settings, state, utils
from dms.ds import Meta

OP = {"==": "__eq__", "!=": "__ne__", "in": "in_", "like": "like", "ilike": "ilike"}

FNS = {
    "uuid": uuid.uuid4,
    "datetime.utcnow": datetime.utcnow,
    "datetime.now": datetime.utcnow,
    "str20": utils.str20,
}


class Query:
    def __init__(self, query: ClauseElement):
        self.query = query
        self.table = query.table if hasattr(query, "table") else query._raw_columns[0]

    async def all(self):
        async with db.database.transaction(force_rollback=True):
            async for record in db.database.iterate(query=self.query):
                yield record

    async def one(self):
        return await db.database.fetch_one(query=self.query)

    async def count(self):
        return (await db.database.fetch_one(query=self.query.alias().count()))._row[
            "tbl_row_count"
        ]

    async def execute(self):
        return await db.database.execute(query=self.query)

    async def paginate(self, page: int = 1, limit: int = settings.PAGE_SIZE):
        query = self.query.offset((max(page, 1) - 1) * limit)
        self.query = query.limit(limit=limit)
        return await db.database.fetch_all(query=self.query)

    def where(self, *args) -> "Query":
        if args and not isinstance(args[0], (tuple, list)):
            args = (args,)
        for f, o, v in args:
            self.query = self.query.where(getattr(self.table.columns[f], OP[o])(v))
        return Query(query=self.query)

    def values(self, **kwargs) -> "Query":
        return Query(query=self.query.values(**kwargs))

    def limit(self, limit) -> "Query":
        return Query(query=self.query.limit(limit=limit))

    def order_by(self, fields: typing.Union[str, typing.Tuple[str]]) -> "Query":
        fields = (fields,) if isinstance(fields, str) else fields
        ordering = []

        for field in fields:
            fn = field
            dir = "+"

            if field[0] in ("-", "+", " "):
                dir = ["-", dir][field[0] in ["+", " "]]
                fn = field[1:]
            ordering.append([desc, asc][dir == "+"](self.table.columns[fn]))

        return Query(query=self.query.order_by(*ordering))


class Objects:
    def __init__(self, name: str):
        self.table = state.items.table(name=name)
        self.schema = state.items.schema(name=name)

    def select(self) -> Query:
        return Query(query=self.table.select())

    def insert(self) -> Query:
        return Query(query=self.table.insert())

    def update(self) -> Query:
        return Query(query=self.table.update())

    def delete(self) -> Query:
        return Query(query=self.table.delete())

    async def save(self, data: dict) -> typing.Optional[RowProxy]:
        if not data:
            return None

        values = {}
        autos = {
            "datetime.utcnow": datetime.utcnow(),
            "datetime.now": datetime.now(),
            "date.today": date.today(),
        }

        for fn, field in self.schema.fields.items():

            if field.is_readonly is True and field.is_nullable:
                continue

            value = data[fn]

            if value is None and not field.is_nullable and field.default is not None:
                value = autos.get(self.schema.meta.defaults[fn]) or field.default()

            if field.onupdate is not None:
                value = autos.get(self.schema.meta.updates[fn]) or field.default()

            values[fn] = value

        pkv = data.get(self.schema.pk.name)
        if pkv is None:
            pkv = values[self.schema.pk.name]
            query = self.insert()
        else:
            query = self.update().where(self.schema.pk.name, "==", pkv)

        await query.values(**values).execute()
        return await self.select().where(self.schema.pk.name, "==", pkv).one()

    def search(
        self, q: str, fields: typing.Union[typing.List[str], typing.Tuple[str]] = None
    ) -> Query:
        query = self.table.select()
        query = query.where(
            sqlalchemy.or_(
                getattr(self.table.columns[f], "ilike")(f"%{q}%") for f in fields
            )
        )
        return Query(query=query)

    def query(self) -> Query:
        return Query(query=self.table.select())


class Model:
    def __init__(self, name: str, meta: Meta):
        self.name = name
        self.meta = meta

    @property
    def objects(self) -> Objects:
        return Objects(name=self.name)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
