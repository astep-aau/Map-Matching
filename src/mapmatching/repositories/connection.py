import psycopg


from mapmatching.repositories.config import Settings


#opens a connection to Postgres with settings provided in config.py
def connect(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
