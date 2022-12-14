class TableCreator:
    def create_tables(self, connection):
        cursor = connection.cursor
        cursor.execute('''
          CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR ( 50 ) NOT NULL UNIQUE,
            password TEXT NOT NULL
            );
            ''')
        cursor.execute('''
          CREATE TABLE IF NOT EXISTS timestables (
            id SERIAL PRIMARY KEY,
            name VARCHAR ( 50 ) NOT NULL,
            bronze BOOLEAN,
            silver BOOLEAN,
            gold BOOLEAN,
            user_id INT NOT NULL,
            CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id)
            );
            ''')
        cursor.execute('''
          CREATE TABLE IF NOT EXISTS factors_learned (
            id SERIAL PRIMARY KEY,
            factor INT,
            times_learned INT,
            timestable_id INT NOT NULL,
            CONSTRAINT fk_timestable FOREIGN KEY(timestable_id) REFERENCES timestables(id)
            );
            ''')

        
