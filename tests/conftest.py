import os  # isort:skip

DATABASES = ["postgresql://postgres@localhost:5432/dms-test", "sqlite:///dms-test.db"]
os.environ["DMS_DATABASE"] = DATABASES[0]  # isort:skip

import pytest
from starlette.testclient import TestClient

from dms import app


@pytest.fixture(scope="module", autouse=True)
def databases():
    return DATABASES


@pytest.fixture()
def client():
    with TestClient(app=app.app) as client:
        yield client
