from starlette.config import Config
from starlette.datastructures import URL, CommaSeparatedStrings as CSS, Secret

config = Config(".env")

CONFIG = config("DMS_CONFIG", cast=str, default="dms.json")
STORAGE = config("DMS_STORAGE", cast=str, default="dms.db")
DEBUG = config("DMS_DEBUG", cast=bool, default=False)
TESTING = config("DMS_TESTING", cast=bool, default=False)
HOST = config("DMS_HOST", cast=str, default="localhost")
PORT = config("DMS_PORT", cast=int, default=8000)
SECRET_KEY = config("DMS_SECRET_KEY", cast=Secret)
ALLOWED_HOSTS = config("DMS_ALLOWED_HOSTS", cast=CSS, default="localhost")
ADMIN = config("DMS_ADMIN", cast=str, default=None)
DATABASE = config("DMS_DATABASE", cast=URL)
PAGE_SIZE = config("DMS_PAGE_SIZE", cast=int, default=50)
ACCESS_LOG = config("DMS_ACCESS_LOG", cast=bool, default=True)
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
THEME = "default"
