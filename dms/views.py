import math
import typing
from pathlib import Path

from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy.engine import RowProxy
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.templating import _TemplateResponse as TemplateResponse
from starlette.types import Receive, Scope, Send

from dms import errors, messages, settings, state
from dms.form import Form
from dms.template import templates


class View(HTTPEndpoint):
    name: typing.Optional[str]
    template: typing.Optional[str] = None

    async def dispatch(self) -> typing.Optional[RedirectResponse]:
        try:
            return await super().dispatch()
        except errors.ObjectNotFound:
            raise HTTPException(status_code=404)

    async def render(self, request: Request, context: dict = None) -> TemplateResponse:
        context = {
            "request": request,
            **(context or {}),
            **{
                "menu": {
                    "is_open": request.cookies.get("menu") != "0",
                    "entries": [
                        {
                            "name": model.meta.name,
                            "path": f"/{name}/",
                            "active": model.name == getattr(self, "name", 0),
                            "icon": model.meta.icon,
                        }
                        for name, model in state.items.models().items()
                    ],
                },
                "messages": messages.get(request=request),
                "ui": {
                    "font": "Open Sans",  # Montserrat
                    "page": f"page-{self.__class__.__name__.lower()}",
                },
            },
        }
        return templates.TemplateResponse(name=self.template, context=context)


class Dashboard(View):
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope, receive, send)
        self.name = self.scope["path"].split("/")[1]
        self.model = state.items.model(name=self.name)
        self.schema = state.items.schema(name=self.name)

    def process(self, record: RowProxy) -> dict:
        data = dict(record._row)
        result = {"_pk": str(data[self.schema.pk.name])}
        for name, field in self.schema.fields.items():
            value = data[name]
            result[name] = {**field.to_dict(), **{"value": value}}
        return result

    def get_url_for_object(self, data: dict = None) -> str:
        if not data:
            return f"/{self.name}/"

        return f"/{self.name}/{data[self.schema.pk.name]}/"

    async def get_object(
        self, id: typing.Union[int, str]
    ) -> typing.Optional[typing.Union[RowProxy, RedirectResponse]]:
        if id == "+":
            return None
        pk = self.schema.pk.name
        result = await self.model.objects.select().where(pk, "==", id).one()
        if result is None:
            raise errors.ObjectNotFound()
        return result

    async def render(self, request: Request, context: dict = None) -> TemplateResponse:
        context = context or {}
        limit = int(request.query_params.get("l") or settings.PAGE_SIZE)
        page = int(request.query_params.get("p") or 1)
        query = request.query_params.get("q") or None
        sort = request.query_params.get("s") or None

        count = context.get("count", 0)
        pages = int(math.ceil(count / limit))

        return await super().render(
            request=request,
            context={
                "request": request,
                "name": self.name,
                "model": self.model.meta.name,
                "icon": self.model.meta.icon,
                "fields": self.schema.field_names,
                "fields_in_list": self.model.meta.list_display,
                "errors": {},
                "path_params": {"id": request.path_params.get("id")},
                "query_params": {"l": limit, "p": page, "q": query, "s": sort},
                "pagination": {
                    "page": page,
                    "prev": max(1, page - 1),
                    "next": min(pages, page + 1),
                    "pages": pages,
                    "count": count,
                },
                **context,
            },
        )


class DashboardModels(Dashboard):
    template = "models.jinja"

    @requires(scopes=["authenticated"], redirect="login")
    async def get(self, request: Request) -> TemplateResponse:
        limit = int(request.query_params.get("l") or settings.PAGE_SIZE)
        page = int(request.query_params.get("p") or 1)
        sort = request.query_params.getlist("s") or self.model.meta.ordering
        q = request.query_params.get("q") or ""

        query = self.model.objects.query()
        if len(q) > 2:
            query = self.model.objects.search(q=q, fields=self.model.meta.search_fields)

        count = await query.count()
        results = [
            self.process(record=o)
            for o in await query.order_by(sort).paginate(page=page, limit=limit)
        ]

        context = {"results": results, "count": count}
        return await self.render(request=request, context=context)


class DashboardModel(Dashboard):
    template = "model.jinja"

    @requires(scopes=["authenticated"], redirect="login")
    async def get(self, request: Request) -> TemplateResponse:
        id = request.path_params["id"]
        result = await self.get_object(id=id)
        data = dict(result._row if result else {})
        form = Form(name=self.name, data=data).validate()
        context = {"result": form.result, "errors": form.errors, "is_create": id == "+"}
        return await self.render(request=request, context=context)

    @requires(scopes=["authenticated"], redirect="login")
    async def post(
        self, request: Request
    ) -> typing.Union[RedirectResponse, TemplateResponse]:
        pk = self.schema.pk.name
        id = request.path_params["id"]
        data = dict(await request.form())

        if id and data.get("form:delete") == "delete":
            await self.model.objects.delete().where(pk, "==", id).execute()
            messages.add(request=request, text="Deleted", type=messages.INFO)
            return RedirectResponse(url=self.get_url_for_object(), status_code=302)

        result = await self.get_object(id=id)
        data = {**dict(result._row if result else {}), **data}

        form = Form(name=self.name, data=data).validate()
        if form.is_valid:
            result = await self.model.objects.save(data=form.data)
            data = dict(result._row if result else {})
            messages.add(request=request, text="Saved", type=messages.SUCCESS)
            return RedirectResponse(
                url=self.get_url_for_object(data=data), status_code=302
            )

        context = {"result": form.result, "errors": form.errors, "is_create": id == "+"}
        return await self.render(request=request, context=context)


class Index(View):
    template: str = "index.jinja"

    @requires(scopes=["authenticated"], redirect="login")
    async def get(self, request: Request) -> Response:
        results = []
        for name, model in state.items.models().items():
            results.append(
                {
                    "name": model.meta.name,
                    "path": f"/{name}/",
                    "icon": model.meta.icon,
                    "count": await model.objects.select().count(),
                }
            )
        context = {"results": results}
        return await self.render(request=request, context=context)


class Login(View):
    template: str = "login.jinja"

    async def get(self, request: Request) -> Response:
        request.session.pop("auth", None)
        request.session.pop("user", None)
        storage = Path(settings.STORAGE)
        context = {"is_storage": storage.is_file()}
        return await self.render(request=request, context=context)

    async def post(self, request: Request) -> Response:
        data = dict(await request.form())
        username = data.get("username")
        password = data.get("password")
        password1 = data.get("password1")
        password2 = data.get("password2")

        storage = Path(settings.STORAGE)
        if not storage.is_file():
            if password1 and password1 == password2:
                with open(storage, "w") as f:
                    f.write(f"{username}:{hasher.hash(password1)}")
            return RedirectResponse(url="/", status_code=302)

        if not username or not password:
            return RedirectResponse(url="/", status_code=302)

        request.session.update(auth=f"{username}:{password}")
        return RedirectResponse(url="/", status_code=302)


class Logout(View):
    async def get(self, request: Request) -> Response:
        request.session.clear()
        return RedirectResponse(url="/", status_code=302)


async def NotFound(request: Request, exc: Exception) -> TemplateResponse:
    """
    Return an HTTP 404 page.
    """
    template = "404.jinja"
    context = {"request": request}
    return templates.TemplateResponse(name=template, context=context, status_code=404)


async def ServerError(request: Request, exc: Exception) -> TemplateResponse:
    """
    Return an HTTP 500 page.
    """
    template = "500.jinja"
    context = {"request": request}
    return templates.TemplateResponse(name=template, context=context, status_code=500)
