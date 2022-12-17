class UserRepository:
    def create(self, connection, user):
        cursor = connection.cursor()
        # inserting into users
        sql = '''INSERT INTO users(username, password) VALUES(%s, %s) RETURNING id;'''
        cursor.execute(sql, (user.username, user.password))
        user.id = cursor.fetchone()[0]

        # inserting into timestables
        sql = '''INSERT INTO timestables(name, bronze, silver, gold, times_learned, user_id) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;'''
        for timestable in user.timestables:
            times_learned = []
            for i in range(12):
                times_learned.append(0)
            cursor.execute(sql, (timestable, False, False, False, times_learned, user.id))
            user.timestables[timestable].id = cursor.fetchone()[0]

            # # for each timestable, inserting how many times each factor has been learned
            # sql2 = '''INSERT INTO factors_learned(factor, times_learned, timestable_id) VALUES(%s, 0, %s) RETURNING id;'''
            # for i in range(1, 13):
            #   cursor.execute(sql2, (i, user.timestables[timestable].id))
            #   user.timestables[timestable].factors_learned[i].id = cursor.fetchone()[0]
        
        connection.commit()
        cursor.close()
        
        return user