class User:
    def __init__(self, username, password, timestables):
        self.id = 0
        self.username = username
        self.password = password
        # timestables will be filled like this 
        # {'twos': Timestable(), 'threes': Timestable, ...}
        self.timestables = timestables