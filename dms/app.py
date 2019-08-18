import logging

from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware

from dms import db, logger, middlewares, router, settings, views

app = Starlette(debug=settings.DEBUG, routes=router.routes)
app.add_middleware(
    AuthenticationMiddleware, backend=middlewares.AdminAuthenticationBackend()
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_exception_handler(404, views.NotFound)
app.add_exception_handler(500, views.ServerError)


@app.on_event("startup")
async def startup() -> None:
    logger.setup()
    logging.info("dms: startup")
    await db.database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    logging.info("dms: shutdown")
    await db.database.disconnect()
