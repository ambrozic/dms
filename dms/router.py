import itertools
import typing

from starlette.routing import Route

from dms import state, views

routes: typing.List[Route] = [
    Route(path="/", name="index", endpoint=views.Index, methods=["GET"]),
    Route(path="/login/", name="login", endpoint=views.Login, methods=["GET", "POST"]),
    Route(path="/logout/", name="logout", endpoint=views.Logout, methods=["GET"]),
]

routes += list(
    itertools.chain(
        *[
            (
                Route(
                    path=f"/{name}/", endpoint=views.DashboardModels, methods=["GET"]
                ),
                Route(
                    path=f"/{name}/{{id:str}}/",
                    endpoint=views.DashboardModel,
                    methods=["GET", "POST"],
                ),
            )
            for name in state.items.models()
        ]
    )
)
