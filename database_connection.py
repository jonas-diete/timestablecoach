import psycopg2

class DatabaseConnection:
  def connect(db_host, db_name, db_user, db_password):
    connection = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password)

    cursor = connection.cursor
    print('PostgreSQL database version:')
    cursor.execute('SELECT version()')