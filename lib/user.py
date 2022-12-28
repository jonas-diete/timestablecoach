class User:
    def __init__(self, username, password, timestables, id=0):
        self.id = id
        self.username = username
        self.password = password
        # timestables will be filled like this 
        # {'twos': Timestable(), 'threes': Timestable(), ...}
        self.timestables = timestables