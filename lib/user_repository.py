class UserRepository:
    def create(self, connection, user):
        sql = '''INSERT INTO users(username, password) VALUES(%s, %s) RETURNING id;
        '''
        cursor = connection.cursor()
        cursor.execute(sql, (user.username, user.password))
        user.id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        
        return user.id