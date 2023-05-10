from flask import Flask, redirect, render_template, request, session
from decouple import config
from database.database_connection import DatabaseConnection
from lib.user_repository import UserRepository
from lib.timestable_repository import TimestableRepository
from lib.user import User
from lib.timestable import Timestable
from lib.factor_learned import FactorLearned
import bcrypt
import jsonpickle
app = Flask(__name__)

# getting key for signing the cookies from .env file
app.secret_key = config('COOKIES_KEY')

# Creating database connection object - this can later be used to connect
database_connection = DatabaseConnection()

# creating user repository object
user_repository = UserRepository()

# converts the tt, which is an int written in the url, into a timestable name to use within our user object
def convert_number_to_timestable(number):
    converter = {'2':'twos', '3':'threes', '4':'fours', '5':'fives', '6':'sixes', '7':'sevens', '8':'eights', '9':'nines', '10':'tens', '11':'elevens', '12':'twelves'}
    try: 
        return converter[number]
    except KeyError:
        return None

def check_registration_username(username):
    message = check_username(username)
    if message:
        return message
    else:
        # Checking if username exists already
        if user_repository.get_one(database_connection.connect(), username) != False:
            return "Username exists already. Try again."
    
    # username is valid - returning no errors
    return None

def check_username(username):
    # Checking if username is alphanumeric
    if not username.isalnum():
        return "Only letters or numbers allowed for username. Try again."
    
    # Checking if username has at least 2 characters
    if len(username) < 2:
        return "Please enter a longer username."

    # Checking if username has at most 15 characters
    if len(username) > 15:
        return "Please enter a shorter username."

    # username is valid - returning no errors
    return None

def check_registration_password(password1, password2):
    # Checking if passwords match
    if password1 != password2:
        return "Passwords don't match. Try again."
    
    # Checking other requirements on characters and length
    return check_password(password1)

def check_password(password):
    # Checking there are no spaces in password
    if " " in password:
        return "No spaces allowed in password. Try again."
    
    # Checking new password has at least 4 characters
    if len(password) < 4:
        return "Password must be at least 4 characters long. Try again."

    # Checking new password has 20 character max
    if len(password) > 20:
        return "Password cannot be longer than 20 characters. Try again."
    
    if "<" in password or ">" in password or "(" in password or ")" in password or ";" in password:
        return "Password cannot contain any of these characters: <>();"
    
    # password is valid - returning no errors
    return None

def check_registration_details(username, password1, password2, cookies, terms_and_conditions_agreement):
    # Checking if cookies have been accepted
    if cookies == 'no':
        return "Please accept the cookies."
    
    # Checking if terms and conditions have been agreed to
    if terms_and_conditions_agreement != "agreed":
        return "Please accept the Terms and Conditions."
    
    username_error_message = check_registration_username(username)
    if username_error_message:
        return username_error_message
    
    password_error_message = check_registration_password(password1, password2)
    if password_error_message:
        return password_error_message

    # no errors returned
    return None

def create_new_timestables():
    timestables = {}
    timestables_names = ['twos', 'threes', 'fours', 'fives', 'sixes', 'sevens', 'eights', 'nines', 'tens', 'elevens', 'twelves']
    for name in timestables_names:
        factors_learned = {}
        for i in range(1, 13):
            factors_learned[i] = FactorLearned(i)
        timestables[name] = Timestable(name, factors_learned)
    return timestables

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        if request.form.get("accepted") == "yes":
            session["cookies"] = "yes"

        # checking if cookies are accepted
        if not "cookies" in session:
            return render_template("login.html", login_message = "You must accept the cookies to continue.", cookies = "")
        
        # saving user input
        username_entered = request.form.get("username")
        password_entered = request.form.get("password")

        # checking for error message on username and password
        # this ensures no special characters etc are used to hack database
        if check_username(username_entered) == None and check_password(password_entered) == None:
            
            # trying to load user from database
            user_retrieved = user_repository.get_one(database_connection.connect(), username_entered) 
            
            print(password_entered.encode('utf-8'))
            # checking user exists and password matches database
            if user_retrieved and bcrypt.checkpw(password_entered.encode('utf-8'), user_retrieved.password.encode('utf-8')):
                
                # logging in
                session["user"] = jsonpickle.encode(user_retrieved)
                return redirect("/select")
        
        # username didn't exist or password was wrong
        return render_template("login.html", login_message = "Incorrect username or password. Try again.", cookies = "yes")
        

    elif request.method == 'GET':   
        # deleting user in case we were redirected here after logout
        if "user" in session:
            session.pop("user", default=None) 

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
        terms_and_conditions_agreement = request.form.get("agreement")

        error_message = check_registration_details(new_username, new_pw1, new_pw2, cookies, terms_and_conditions_agreement)
        if error_message:
            return render_template("register.html", register_message = error_message, cookies = cookies)
        
        # REGISTERING NEW USER
        # encrypting password
        salt = bcrypt.gensalt()
        encoded_pw = new_pw1.encode('utf-8')
        hashed_password = bcrypt.hashpw(encoded_pw, salt)

        # creating new user with new timestables dict
        timestables = create_new_timestables()
        new_user = User(new_username, hashed_password.decode(encoding='UTF-8'), timestables)

        # saving new user in database and
        # saving created user in session cookie with newly generated ids
        connection = database_connection.connect()
        session["user"] = jsonpickle.encode(user_repository.create(connection, new_user))
        connection.close()

        return redirect("/select")
    
    elif request.method == 'GET':
        return render_template("register.html", register_message = "Register a new user.", cookies = cookies)

@app.route("/terms", methods=["GET"])
def terms():
    return render_template('terms.html')

@app.route("/select", methods=["GET", "POST"])
def select():
    if not "user" in session or session["user"] == False:
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
                user = jsonpickle.decode(session["user"])
                if user.timestables[timestable_name].gold == True:
                    user_medals_str += '3'
                elif user.timestables[timestable_name].silver == True:
                    user_medals_str += '2'
                elif user.timestables[timestable_name].bronze == True:
                    user_medals_str += '1'
                else:
                    user_medals_str += '0'

            # Loading page
            return render_template("select.html", username = user.username, tts = range(3, 13), medals = user_medals_str)                

@app.route("/test/<tt>", methods=["GET", "POST"])
def test(tt):
    if not "user" in session:
        return redirect("/login")
    else:
        user = jsonpickle.decode(session["user"])
        if request.method == "GET":
            return render_template("test.html", timestable = tt, username = user.username)
        elif request.method == 'POST':
            timestable = convert_number_to_timestable(tt)
            # Receiving which medal was won, when timestable test was completed
            medal_earned = request.form.get("medal_earned")
            if medal_earned == '3':
                user.timestables[timestable].gold = True
            elif medal_earned == '2':
                user.timestables[timestable].silver = True
            elif medal_earned == '1':
                user.timestables[timestable].bronze = True

            # updating user in session cookie
            session["user"] = jsonpickle.encode(user)

            # updating medal in database
            timestable_repo = TimestableRepository()
            timestable_repo.update_medal(database_connection.connect(), user, user.timestables[timestable])
            
            return redirect("/select") 


@app.route("/practise/<tt>", methods=["GET", "POST"])
def practise(tt):
    if not "user" in session:
        return redirect("/login")
    else:
        user = jsonpickle.decode(session["user"])
        timestable = convert_number_to_timestable(tt)

        if request.method == "GET":
            learningdata = ""
            for i in user.timestables[timestable].factors_learned:
                learningdata += str(user.timestables[timestable].factors_learned[i].times_learned)

            # Sending the learning data to be used in practise.html
            return render_template("practise.html", timestable = int(tt), username = session["username"], numbers = range(1,13), learningdata = learningdata)
        
        elif request.method == 'POST': # gets called when a learning cycle is finished

            # getting learning data from website
            learningdata_updated = request.form.get("learningdata_updated")
            times_learned = []
            # global user
            for i in range(12):
                # creating list that can be saved in SQL database
                times_learned.append(int(learningdata_updated[i]))
                # saving the newly learned factors in user object
                user.timestables[timestable].factors_learned[i + 1].times_learned = learningdata_updated[i]
            
            # updating user in session cookie
            session["user"] = jsonpickle.encode(user)

            # updating times_learned in database
            timestable_repo = TimestableRepository()
            timestable_repo.update_factors_learned(database_connection.connect(), user, user.timestables[timestable], times_learned)
        
            return redirect("/select") 

if __name__ == "__main__":
    app.run()