from flask import Flask, redirect, render_template, request, session
from github import Github
from decouple import config
from database.database_connection import DatabaseConnection
from lib.user_repository import UserRepository
from lib.user import User
from lib.timestable import Timestable
from lib.factor_learned import FactorLearned
import bcrypt
app = Flask(__name__)

# getting key for signing the cookies from .env file
app.secret_key = config('COOKIES_KEY')

# getting github auth token from .env file
GITHUB_TOKEN = config('GITHUB_TOKEN')

# access github repo to save data on
github = Github(GITHUB_TOKEN)
repository = github.get_user().get_repo("timestable-coach-data")

# Creating database connection object - this can later be used to connect
database_connection = DatabaseConnection()

# creating user repository object
user_repository = UserRepository()

# defining global user variable, that stores all the user data
user = False

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        if request.form.get("accepted") == "yes":
            session["cookies"] = "yes"

        # checking if cookies are accepted
        if not 'cookies' in session:
            return render_template("login.html", login_message = "You must accept the cookies to continue.", cookies = "")
        
        # saving user input
        username_entered = request.form.get("username")
        password_entered = request.form.get("password")

        # checking if user exists and password is correct
        global user
        user = user_repository.get_one(database_connection.connect(), username_entered) 
        if user == False or not bcrypt.checkpw(password_entered.encode('utf-8'), user.password.encode('utf-8')):
            return render_template("login.html", login_message = "Incorrect username or password. Try again.", cookies = "yes")
        
        # logging in
        session["username"] = user.username
        return redirect("/select")
    
    elif request.method == 'GET':   
        # deleting username in case we were redirected here after logout
        if "username" in session:
            session.pop("username", default=None) 

        # checking if user has accepted cookies
        if "cookies" in session:
            return render_template("login.html", login_message = "Enter your login details.", cookies = "yes")
        else:
            return render_template("login.html", login_message = "Enter your login details.", cookies = "")

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'cookies' in session:
        cookies = 'yes'
    else:
        cookies = 'no'

    if request.method == "POST":

        # getting user data
        new_username = request.form.get("username")
        new_pw1 = request.form.get("password1")
        new_pw2 = request.form.get("password2")

        if cookies == 'no':
            return render_template("register.html", register_message = "Please accept the cookies.", cookies = cookies)

        if user_repository.get_one(database_connection.connect(), new_username) != False:
            return render_template("register.html", register_message = "Username exists already. Try again.", cookies = cookies)
        
        # Checking if terms and conditions have been agreed to
        if request.form.get("agreement") != "agreed":
            return render_template("register.html", register_message = "Please accept the Terms and Conditions.", cookies = cookies)

        # Checking if username is alphanumeric
        if not new_username.isalnum():
            return render_template("register.html", register_message = "Only letters or numbers allowed for username. Try again.", cookies = cookies)
        
        # Checking if username has at least 2 characters
        if len(new_username) < 2:
            return render_template("register.html", register_message = "Please enter a longer username.", cookies = cookies)

        # Checking if passwords match
        if new_pw1 != new_pw2:
            return render_template("register.html", register_message = "Passwords don't match. Try again.", cookies = cookies)
        
        # Checking there are no spaces in password
        if " " in new_pw1:
            return render_template("register.html", register_message = "No spaces allowed in password. Try again.", cookies = cookies)
        
        # Checking new password has at least 4 characters
        if len(new_pw1) < 4:
            return render_template("register.html", register_message = "Password must be at least 4 characters long. Try again.", cookies = cookies)
        
        # REGISTERING NEW USER
        # encrypting password
        salt = bcrypt.gensalt()
        encoded_pw = new_pw1.encode('utf-8')
        hashed_password = bcrypt.hashpw(encoded_pw, salt)

        # connecting with database
        connection = database_connection.connect()
        
        # creating a user object, filling it with TimesTable objects and those with FactorsLearned objects
        timestables = {}
        timestables_names = ['twos', 'threes', 'fours', 'fives', 'sixes', 'sevens', 'eights', 'nines', 'tens', 'elevens', 'twelves']
        for name in timestables_names:
            factors_learned = {}
            for i in range(1, 13):
                factors_learned[i] = FactorLearned(i)
            timestables[name] = Timestable(name, factors_learned)
        global user
        user = User(new_username, hashed_password.decode(encoding='UTF-8'), timestables)

        # saving new user in database and
        # updating the user object with the correct ids generated from the database
        user = user_repository.create(connection, user)

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

        # closing database connection
        connection.close()

        # Logging in
        session["username"] = new_username
        return redirect("/select")
    
    elif request.method == 'GET':
        return render_template("register.html", register_message = "Register a new user.", cookies = cookies)

@app.route("/terms", methods=["GET"])
def terms():
    return render_template('terms.html')

@app.route("/select", methods=["GET", "POST"])
def select():
    global user
    if not "username" in session or user == False:
        return redirect("/login")
    else:
        if request.method == "POST":

            # Saving the timestable the user has selected
            tt_selected = request.form.get("timestable")

            # Checking if "test" or "practise" has been clicked
            if request.form.get("test_practise") == "test":
                return redirect("/test/" + tt_selected)
            else:
                return redirect("/practise/" + tt_selected)
        
        # filling user_medals_string so it is a string of 0, 1, 2, or 3s 
        # each indicating which medal has been earned for this timestable
        # '02301102021' means no medals for the twos, a silver for the threes, 
        # a gold for the fours, no medals for the fives, etc.
        elif request.method == "GET":
            timestables_names = ['twos', 'threes', 'fours', 'fives', 'sixes', 'sevens', 'eights', 'nines', 'tens', 'elevens', 'twelves']
            user_medals_str = ""
            for timestable_name in timestables_names:
                if user.timestables[timestable_name].gold == True:
                    user_medals_str += '3'
                elif user.timestables[timestable_name].silver == True:
                    user_medals_str += '2'
                elif user.timestables[timestable_name].bronze == True:
                    user_medals_str += '1'
                else:
                    user_medals_str += '0'

            # Loading page
            return render_template("select.html", username = session["username"], tts = range(3, 13), medals = user_medals_str)                
          

            # # OLD CODE DELETE LATER
            # # Getting medal-data from file saved on github and saving it in user_medals
            # user_medals_str = ""
            # file = repository.get_contents("medals.txt")
            # for row in file.decoded_content.decode().split("\n"):
            #     # Searching for username and checking there is not a longer username which includes the current one
            #     if session["username"] in row and len(row) == len(session["username"]) + 11:
            #         user_medals_str = row[len(session["username"]):]

@app.route("/test/<tt>", methods=["GET", "POST"])
def test(tt):
    if not "username" in session:
        return redirect("/login")
    else:
        if request.method == "GET":
            return render_template("test.html", timestable = tt, username = session["username"])
        elif request.method == 'POST':
            
            # converting the tt, which is an int, into a timestable name to use within our user object
            converter = {2:'twos', 3:'threes', 4:'fours', 5:'fives', 6:'sixes', 7:'sevens', 8:'eights', 9:'nines', 10:'tens', 11:'elevens', 12:'twelves'}
            tt = converter[tt]
            
            # Receiving which medal was won, when timestable test was completed
            medal_earned = request.form.get("medal_earned")
            global user
            if medal_earned == 3:
                user.timestables[tt].gold == True
            elif medal_earned == 2:
                user.timestables[tt].silver == True
            elif medal_earned == 1:
                user.timestables[tt].bronze == True

            # Todo:
            # Save new medal updates in database


            # OLD CODE DELETE LATER
            # if int(medal_earned) > 0:
            #     # Saving all medals from all users from file into all_medals dictionary
            #     all_medals = {}
            #     file = repository.get_contents("medals.txt")
            #     for row in file.decoded_content.decode().split("\n"):
            #         medals_of_user = []
            #         medals_of_user_str = row[len(row) - 11:]
            #         for i in medals_of_user_str:
            #             medals_of_user.append(i)
            #         all_medals[row[:len(row) - 11]] = medals_of_user

            #     # Updating all_medals with the medal earned from current user and current timestable
            #     for user in all_medals:
            #         # Checking if new medal is actually better than the old one
            #         if user == session["username"] and all_medals[user][int(tt) - 2] < medal_earned:
            #             all_medals[user][int(tt) - 2] = medal_earned

            #     # Overwriting whole content of text file with updated all_medals
            #     file = repository.get_contents("medals.txt")
            #     updated_file = ""
            #     for user in all_medals:
            #         medals_of_user_str = ""
            #         for medal in all_medals[user]:
            #             medals_of_user_str += medal
            #         updated_file += user + medals_of_user_str + "\n"
            #     repository.update_file(file.path, "Overwriting medals.txt", updated_file, file.sha)
            
            return redirect("/select") 


@app.route("/practise/<tt>", methods=["GET", "POST"])
def practise(tt):
    if not "username" in session:
        return redirect("/login")
    else:
        # Page is loaded normally
        if request.method == "GET":
            # Getting the data about which facts have been learned from the selected timestable
            learningdata = ""
            x = 0
            file = repository.get_contents("learning.txt")
            for row in file.decoded_content.decode().split("\n"):
                if row:
                    # Finding correct timestable row
                    if x == int(tt):
                        for item in row:
                            learningdata += item
                        break
                    else:
                        if x > 0:
                            x += 1
                    # Finding correct user
                    if row == session["username"]:
                        x = 2
                        
            # Sending the learning data to be used in practise.html
            return render_template("practise.html", timestable = int(tt), username = session["username"], numbers = range(1,13), learningdata = learningdata)
        
        # Data has been received through POST
        else:
            learningdata_updated = request.form.get("learningdata_updated")
            
            updated_file = ""
            learning_information = []
            # Getting current learning information from github
            file = repository.get_contents("learning.txt")
            for row in file.decoded_content.decode().split("\n"):
                learning_information.append(row)

            for i in range(len(learning_information)):
                if learning_information[i] == session["username"]:
                    learning_information[i + int(tt) - 1] = learningdata_updated

            for item in learning_information:
                updated_file += item + "\n"

            repository.update_file(file.path, "Overwriting learning.txt", updated_file, file.sha)
        
            return redirect("/select") 

if __name__ == "__main__":
    app.run()