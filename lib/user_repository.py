class UserRepository:
    def create(self, connection, user):
        cursor = connection.cursor()
        # inserting into users
        sql = '''INSERT INTO users(username, password) VALUES(%s, %s) RETURNING id;'''
        cursor.execute(sql, (user.username, user.password))
        user.id = cursor.fetchone()[0]

        # inserting into timestables
        sql = '''INSERT INTO timestables(name, bronze, silver, gold, user_id) VALUES(%s, %s, %s, %s, %s) RETURNING id;'''
        for timestable in user.timestables:
            cursor.execute(sql, (timestable, False, False, False, user.id))
            user.timestables[timestable].id = cursor.fetchone()[0]

        # todo: inserting into factors_learned

        connection.commit()
        cursor.close()
        
        return user.id