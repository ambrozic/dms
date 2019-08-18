import uvicorn

from dms import app, settings


def main() -> None:
    uvicorn.run(
        app=app.app,
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
        access_log=settings.ACCESS_LOG,
    )
