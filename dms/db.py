import databases
import sqlalchemy

from dms import settings

url = str(settings.DATABASE)
database: databases.Database = databases.Database(settings.DATABASE)
metadata = sqlalchemy.MetaData()
