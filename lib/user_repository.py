from lib.user import User
from lib.timestable import Timestable
from lib.factor_learned import FactorLearned

class UserRepository:
    def create(self, connection, user):
        cursor = connection.cursor()
        # inserting into users
        sql = '''INSERT INTO users(username, password) VALUES(%s, %s) RETURNING id;'''
        cursor.execute(sql, (user.username, user.password))
        user.id = cursor.fetchone()[0]

        # inserting into timestables
        sql = '''INSERT INTO timestables(name, bronze, silver, gold, personal_best, times_learned, user_id) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id;'''
        for timestable in user.timestables:
            times_learned = []
            for i in range(12):
                times_learned.append(0)
            cursor.execute(sql, (timestable, False, False, False, 0, times_learned, user.id))
            user.timestables[timestable].id = cursor.fetchone()[0]
        
        connection.commit()
        cursor.close()
        
        return user

        
    def get_one(self, connection, username):
        cursor = connection.cursor()
        user_name = username
        sql = '''SELECT * FROM users WHERE username = %s;'''
        cursor.execute(sql, (user_name,))
        user_from_db = cursor.fetchone()

        # user doesn't exist
        if user_from_db == None:
            return False

        # storing id and password temporarily
        user_id = user_from_db[0]
        password = user_from_db[2]

        sql = '''SELECT * FROM timestables WHERE user_id = %s;'''
        cursor.execute(sql, (user_id,))
        all_timestables = cursor.fetchall()

        # Creating timestables dictionary
        timestables = {}
        for i in range(11):
            timestable_from_db = all_timestables[i]       
            # creating factors_learned dictionary filled with FactorsLearned objects
            factors_learned = {}
            for j in range(len(timestable_from_db[6])):
              factors_learned[j + 1] = FactorLearned(j + 1, timestable_from_db[6][j])

            # creating new Timestable object
            timestables[timestable_from_db[1]] = Timestable(timestable_from_db[1], factors_learned, timestable_from_db[4], timestable_from_db[3], timestable_from_db[2], timestable_from_db[5], timestable_from_db[0])

        connection.commit()
        cursor.close()
        
        user = User(username, password, timestables, user_id)
        return user