from flask import Flask, redirect, render_template, request, session
import csv
app = Flask(__name__)

# Key for signing the cookies
app.secret_key = "SANDY_CANYON_SUNSET"

# Global Variables
# timestable that was selected
tt = 0
# username that logged in
username = ""

user_medals_str = ""

# Message displayed on login page
login_message = "Enter your login details."
# Message displayed on register page
register_message = "Register"

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Reading CSV file and creating a users dictionary with usernames and passwords
        users = {}
        with open("data/users.csv", "r", newline="") as usernamefile:
            userreader = csv.reader(usernamefile, delimiter=" ")
            for row in userreader:
                if row:     # This is checking if the row is "true", i.e. not empty
                    users[row[0]] = row[1]
        
        # checking if username is in users and if the password is matching
        username_entered = request.form.get("username")
        if username_entered in users and request.form.get("password") == users[username_entered]:

            # Saving username in session cookie
            session["username"] = username_entered

            # Saving username in global variable
            #global username
            #username = username_entered

            # Changing message, ready for next login
            global login_message
            login_message = "Enter your login details."
            return redirect("/select")
        else:
            return render_template("login.html", login_message = "Incorrect username or password. Try again.")
    else:    
        global register_message
        register_message = "Register"
        if "username" in session:
            session.pop("username", default=None) # Deleting username in case we were redirected here after logout
        #username = ""   # In case we were redirected here after logout
        return render_template("login.html", login_message = login_message)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_pw1 = request.form.get("password1")
        new_pw2 = request.form.get("password2")
        
        # Checking if username exists already
        users = {}
        with open("data/users.csv", "r", newline="") as usernamefile:
            userreader = csv.reader(usernamefile, delimiter=" ")
            for row in userreader:
                if row:     # This is checking if the row is "true", i.e. not empty
                    users[row[0]] = row[1]
        if not new_username in users:
            # Checking if username is alphanumeric:
            if new_username.isalnum():
                # Checking if username has at least 2 characters
                if len(new_username) > 1:
                    # Checking if passwords match
                    if new_pw1 == new_pw2:
                        # Checking there are no spaces in password
                        if not (" " in new_pw1):
                            # Checking if password has at least 4 characters
                            if len(new_pw1) > 3:
                                    # Saving new username and password in CSV file
                                    with open("data/users.csv", "a", newline="") as usernamefile:
                                        userwriter = csv.writer(usernamefile, delimiter=" ")
                                        userwriter.writerow([new_username, new_pw1])
                                    
                                    # Adding entry in medals CSV file for the new user
                                    # 0 = no medals, 1 = bronze, 2 = silver, 3 = gold
                                    # Arranged in order of timestables, starting with 2x
                                    with open("data/medals.csv", "a", newline="") as medalsfile:
                                        medalswriter = csv.writer(medalsfile, delimiter=" ")
                                        medalswriter.writerow([new_username, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                                    
                                    global login_message 
                                    login_message = "New user created. Please login."
                                    return redirect("/login")
                            else:
                                global register_message
                                register_message = "Password needs to be at least 4 characters long. Try again."
                                return redirect("/register")
                        else:
                            register_message = "No spaces allowed in password. Try again."
                            return redirect("/register")
                    else:
                        register_message = "Passwords don't match. Try again."
                        return redirect("/register")
                else:
                    register_message = "Please enter a longer username."
                    return redirect("/register")
            else: 
                register_message = "Only letters or numbers allowed for username. Try again."
                return redirect("/register")
        else:
            register_message = "Username exists already. Try again."
            return redirect("/register")
    else:
        login_message = "Enter your login details."
        return render_template("register.html", register_message = register_message)

@app.route("/select", methods=["GET", "POST"])
def select():
    
    if not "username" in session:
    #if username == "":
        return redirect("/login")
    else:
        if request.method == "POST":
                
            # Saving the timestable the user has selected
            global tt
            tt = int(request.form.get("timestable"))

            # Checking if "test" or "practise" has been clicked
            if request.form.get("test_practise") == "test":
                return redirect("/test")
            else:
                return redirect("/practise")
        
        else:
            # Getting medal-data and saving it in user_medals
            with open("data/medals.csv", "r", newline="") as medalsfile:
                medalsreader = csv.reader(medalsfile, delimiter=" ")
                for row in medalsreader:
                    if row[0] == session["username"]:
                    #if row[0] == username:
                        #global user_medals_str
                        user_medals_str = ""
                        for i in range(11):
                            user_medals_str += (row[i + 1])

            # Loading page
            return render_template("select.html", username = session["username"], tts = range(3, 13), medals = user_medals_str)
    

@app.route("/test", methods=["GET", "POST"])
def test():
    if not "username" in session:
    #if username == "":
        return redirect("/login")
    else:
        if request.method == "GET":
            return render_template("test.html", timestable = tt, username = session["username"])
        else:
            # Receiving which medal was won, when timestable test was completed
            medal_earned = request.form.get("medal_earned")
            
            if int(medal_earned) > 0:
                # Saving all medals from all users from file into all_medals
                all_medals = []
                with open("data/medals.csv", "r", newline="") as medalsfile:
                    medalsreader = csv.reader(medalsfile, delimiter=" ")
                    for row in medalsreader:
                        all_medals.append(row)

                # Updating all_medals with the medal earned from current user and current timestable
                for row in all_medals:
                    if row[0] == session["username"]:
                        row[tt - 1] = medal_earned

                # Overwriting content of CSV file with updated all_medals
                with open("data/medals.csv", "w", newline="") as medalsfile:
                    medalswriter = csv.writer(medalsfile, delimiter=" ")
                    for row in all_medals:
                        medalswriter.writerow(row)

            return redirect("/select")


@app.route("/practise", methods=["GET", "POST"])
def practise():
    if not "username" in session:
    #if username == "":
        return redirect("/login")
    else:
        return render_template("practise.html", timestable = tt, username = session["username"])

if __name__ == "__main__":
    app.run()