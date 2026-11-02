import psycopg

class BaseRepository:
    def __init__(self, connection: psycopg.Connection):
        self.connection = connection

    def fetch(self, query: str, params: tuple = ()) -> list[tuple]:
        #we try executing a given query, if it fails, then we make sure to close the opened cursor.
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def test_repo(self) -> str:
        raise NotImplementedError(f"{type(self).__name__} did not implement the function test_repo(self) -> str: fix it!")