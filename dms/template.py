import json
import os
import typing
from datetime import date, datetime
from urllib.parse import urlencode

import jinja2
from starlette.templating import Jinja2Templates

from dms import settings


def qsu(d, k, v):
    return urlencode({kk: vv for kk, vv in {**d, **{k: v}}.items() if vv})


def to_date(v: date):
    return v.strftime(settings.DATE_FORMAT) if v else ""


def to_datetime(v: datetime):
    return v.strftime(settings.DATETIME_FORMAT) if v else ""


def to_empty(v: typing.Any):
    return v if v else ""


def to_json(v: dict):
    return json.dumps(obj=v, indent=4, default=str) if v else None


class Templates(Jinja2Templates):
    def get_env(self, directory: str) -> "jinja2.Environment":
        @jinja2.contextfunction
        def url_for(context: dict, name: str, **path_params: typing.Any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        loader = jinja2.FileSystemLoader(directory)
        env = jinja2.Environment(
            loader=loader, autoescape=True, trim_blocks=True, lstrip_blocks=True
        )
        env.globals["url_for"] = url_for
        env.filters.update(
            qsu=qsu,
            to_date=to_date,
            to_datetime=to_datetime,
            to_empty=to_empty,
            to_json=to_json,
        )
        return env


templates = Templates(
    directory=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), f"templates/{settings.THEME}"
    )
)
