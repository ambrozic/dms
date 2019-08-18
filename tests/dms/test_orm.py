from datetime import date, datetime

import pytest
import sqlalchemy as sa
import sqlalchemy_utils as sau

from dms.state import Loader

metadata = sa.MetaData()
items = sa.Table(
    "items",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("date", sa.Date(), default=date.today),
    sa.Column("datetime", sa.DateTime(), default=datetime.utcnow),
    sa.Column("flag", sa.Boolean()),
    sa.Column("float", sa.Float()),
    sa.Column("integer", sa.Integer()),
    sa.Column("json", sa.JSON()),
    sa.Column("number", sa.Numeric()),
    sa.Column("string", sa.String(length=100)),
    sa.Column("text", sa.Text()),
    sa.Column("time", sa.Time()),
)


@pytest.fixture(scope="module", autouse=True)
def create(databases):
    for url in databases:
        if not sau.database_exists(url=url):
            sau.create_database(url=url)
        engine = sa.create_engine(url)
        metadata.create_all(engine)
    yield
    for url in databases:
        engine = sa.create_engine(url)
        metadata.drop_all(engine)
        if sau.database_exists(url=url):
            sau.drop_database(url=url)


@pytest.mark.asyncio
async def test():
    source = {
        "models": {
            "item": {
                "table": "items",
                "icon": "sitemap",
                "list_display": [
                    "uid",
                    "name",
                    "number",
                    "desc",
                    "data",
                    "active",
                    "date_created",
                    "date_updated",
                ],
            }
        }
    }
    loader = Loader(source=source)
    schema = loader.schema(name="item")
    assert schema.meta.table == "items"
    assert "string" in schema.fields
