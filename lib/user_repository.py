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
        sql = '''INSERT INTO timestables(name, bronze, silver, gold, times_learned, user_id) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;'''
        for timestable in user.timestables:
            times_learned = []
            for i in range(12):
                times_learned.append(0)
            cursor.execute(sql, (timestable, False, False, False, times_learned, user.id))
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
        timestables_names = ['twos', 'threes', 'fours', 'fives', 'sixes', 'sevens', 'eights', 'nines', 'tens', 'elevens', 'twelves']
        timestables = {}
        for i in range(len(timestables_names)):
            timestable_from_db = all_timestables[i]

            # creating factors_learned dictionary filled with FactorsLearned objects
            factors_learned = {}
            for j in range(len(timestable_from_db[5])):
              factors_learned[j + 1] = FactorLearned(j + 1, timestable_from_db[5][j])

            # creating new Timestable object
            timestables[timestables_names[i]] = Timestable(timestable_from_db[1], factors_learned, timestable_from_db[2], timestable_from_db[3], timestable_from_db[4], timestable_from_db[0])

        connection.commit()
        cursor.close()
        
        user = User(username, password, timestables, user_id)

        # printing the user to check what's saved
        print(f'ID: {user.id}')
        print(f'Username: {user.username}')
        print(f'Password: {user.password}')
        for timestable in user.timestables:
            print(f'Timestable ID: {user.timestables[timestable].id}')
            print(f'Timestable name: {user.timestables[timestable].name}')
            print(f'Timestable gold: {user.timestables[timestable].gold}')
            print(f'Timestable silver: {user.timestables[timestable].silver}')
            print(f'Timestable bronze: {user.timestables[timestable].bronze}')
            for factor_learned in user.timestables[timestable].factors_learned:
                print(f'Factor Learned factor: {user.timestables[timestable].factors_learned[factor_learned].factor}')
                print(f'Factor Learned times_learned: {user.timestables[timestable].factors_learned[factor_learned].times_learned}')
        return user