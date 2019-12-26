# dms
Database Management Service dashboard

## Features
- standalone and independent as a service
- only a simple json configuration for dashboard
- no database model definitions written in python
- very generic from database perspective
- limited to `uuid` and `integer` for primary keys values
- limited to `datetime` or `date` for auto created or updated field values
- support for sqlite and postgres
- use as a docker container


## Configuration
### Dashboard
For an example dashboard configuration look at [docs/dms.json](https://github.com/ambrozic/dms/blob/master/docs/dms.json).

### Service
Service configuration can be done using environmental variables or by `.env` file mounted into container. 


## Usage
Simple docker compose configuration

```
services:
  dms:
    image: ambrozic/dms:latest
    ports:
      - "8000:8000"
    volumes:
      - /path/to/your/dms.json:/srv/app/dms.json
    environment:
      - DMS_HOST=0.0.0.0
      - DMS_SECRET_KEY=<secret-key>
      - DMS_DATABASE=postgresql://postgres@db:5432/db
```

and open `http://0.0.0.0:8000`

## Screenshots
[here](https://raw.githubusercontent.com/ambrozic/dms/master/docs/ss.png)
