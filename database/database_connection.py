import psycopg2
from decouple import config

class DatabaseConnection:
    def connect(self):
        try:
            connection = psycopg2.connect(
            host=config('DB_HOST'),
            database=config('DB_NAME'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'))

            return connection
        except (Exception, psycopg2.DatabaseError) as error:
          print(error)
