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
            name VARCHAR ( 10 ) NOT NULL,
            bronze BOOLEAN,
            silver BOOLEAN,
            gold BOOLEAN,
            times_learned int[],
            user_id INT NOT NULL,
            CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id)
            );
            ''')
            # times_learned is an array, stating how many times each factor 
            # of the timestable was learned correctly - 
            # starting from x1 up to x12
            # [3, 0, 2, etc.] means the current timestable * 1 was correctly 
            # practised 3 times, * 2 was practised correctly 0 times, 
            # * 3 was practised correctly 2 times, etc.

        # cursor.execute('''
        #   CREATE TABLE IF NOT EXISTS factors_learned (
        #     id SERIAL PRIMARY KEY,
        #     factor INT,
        #     times_learned INT,
        #     timestable_id INT NOT NULL,
        #     CONSTRAINT fk_timestable FOREIGN KEY(timestable_id) REFERENCES timestables(id)
        #     );
        #     ''')

        
