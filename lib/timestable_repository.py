from lib.user import User
from lib.timestable import Timestable
from lib.factor_learned import FactorLearned

class TimestableRepository:
    # the timestable object that's passed in here should have the new medal already saved
    def update_medal(self, connection, user, timestable):
        cursor = connection.cursor()

        if timestable.gold == True:
            sql = '''UPDATE timestables SET gold = true WHERE user_id = %s AND name = %s'''
        elif timestable.silver == True:
            sql = '''UPDATE timestables SET silver = true WHERE user_id = %s AND name = %s'''
        elif timestable.bronze == True:
            sql = '''UPDATE timestables SET bronze = true WHERE user_id = %s AND name = %s'''
        
        cursor.execute(sql, (user.id, timestable.name))
        
        connection.commit()
        cursor.close()

    def update_factors_learned(self, connection, user, timestable, times_learned):
        cursor = connection.cursor()
        
        sql = '''UPDATE timestables SET times_learned = %s WHERE user_id = %s AND name = %s'''
        cursor.execute(sql, (times_learned, user.id, timestable.name))

        connection.commit()
        cursor.close()