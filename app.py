from flask import Flask, redirect, render_template, request, session
import csv
app = Flask(__name__)

# Key for signing the cookies
app.secret_key = "SANDY_CANYON_SUNSET"

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("accepted") == "yes":
            session["cookies"] = "yes"
        # Reading CSV file and creating a users dictionary with usernames and passwords
        users = {}
        with open("data/users.csv", "r", newline="") as usernamefile:
            userreader = csv.reader(usernamefile, delimiter=" ")
            for row in userreader:
                if row:     # This is checking if the row is "true", i.e. not empty
                    users[row[0]] = row[1]
        
        # Checking if cookies have been accepted
        if "cookies" in session:   

            # checking if username is in users and if the password is matching 
            username_entered = request.form.get("username")
            if username_entered in users and request.form.get("password") == users[username_entered]:
                
                # Saving username in session cookie
                session["username"] = username_entered
                return redirect("/select")
            else:
                return render_template("login.html", login_message = "Incorrect username or password. Try again.", cookies = "yes")
        else:
            return render_template("login.html", login_message = "You must accept the cookies to continue.", cookies = "")
    
    else:    
        # Deleting username in case we were redirected here after logout
        if "username" in session:
            session.pop("username", default=None) 

        # Checking if user has accepted cookies
        if "cookies" in session:
            return render_template("login.html", login_message = "Enter your login details.", cookies = "yes")
        else:
            return render_template("login.html", login_message = "Enter your login details.", cookies = "")

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
        if request.form.get("agreement") != "agreed":
            return render_template("register.html", register_message = "Please accept the Terms and Conditions.")

        elif new_username in users:
            return render_template("register.html", register_message = "Username exists already. Try again.")
        
        # Checking if username is alphanumeric
        elif not new_username.isalnum():
            return render_template("register.html", register_message = "Only letters or numbers allowed for username. Try again.")
        
        # Checking if username has at least 2 characters
        elif len(new_username) < 2:
            return render_template("register.html", register_message = "Please enter a longer username.")

        # Checking if passwords match
        elif new_pw1 != new_pw2:
            return render_template("register.html", register_message = "Passwords don't match. Try again.")
        
        # Checking there are no spaces in password
        elif " " in new_pw1:
            return render_template("register.html", register_message = "No spaces allowed in password. Try again.")
        
        # Checking new password has at least 4 characters
        elif len(new_pw1) < 4:
            return render_template("register.html", register_message = "Password must be at least 4 characters long. Try again.")
        
        else:
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

            # Checking if user has accepted cookies
            if "cookies" in session:
                return render_template("login.html", login_message = "New user created. Please Login.", cookies = "yes")
            else:
                return render_template("login.html", login_message = "New user created. Please Login.", cookies = "")             
        
    else:
        return render_template("register.html", register_message = "Register a new user.")

@app.route("/terms", methods=["GET"])
def terms():
    return render_template('terms.html')

@app.route("/select", methods=["GET", "POST"])
def select():
    
    if not "username" in session:
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
        
        else:
            # Getting medal-data and saving it in user_medals
            with open("data/medals.csv", "r", newline="") as medalsfile:
                medalsreader = csv.reader(medalsfile, delimiter=" ")
                for row in medalsreader:
                    if row[0] == session["username"]:
                        user_medals_str = ""
                        for i in range(11):
                            user_medals_str += (row[i + 1])

            # Loading page
            return render_template("select.html", username = session["username"], tts = range(3, 13), medals = user_medals_str)
    

@app.route("/test/<tt>", methods=["GET", "POST"])
def test(tt):
    if not "username" in session:
        return redirect("/login")
    else:
        if request.method == "GET":
            return render_template("test.html", timestable = tt, username = session["username"])
        else:  # Data was sent through POST
            # Receiving which medal was won, when timestable test was completed
            medal_earned = request.form.get("medal_earned")
            
            if int(medal_earned) > 0:
                # Saving all medals from all users from file into all_medals variable
                all_medals = []
                with open("data/medals.csv", "r", newline="") as medalsfile:
                    medalsreader = csv.reader(medalsfile, delimiter=" ")
                    for row in medalsreader:
                        all_medals.append(row)

                # Updating all_medals with the medal earned from current user and current timestable
                for row in all_medals:
                    # Checking if new medal is actually better than the old one
                    if row[0] == session["username"] and row[int(tt) - 1] < medal_earned:
                        row[int(tt) - 1] = medal_earned

                        # Overwriting content of CSV file with updated all_medals
                        with open("data/medals.csv", "w", newline="") as medalsfile:
                            medalswriter = csv.writer(medalsfile, delimiter=" ")
                            for row in all_medals:
                                medalswriter.writerow(row)

            return redirect("/select") # Doesn't work! Getting back with back button instead.


@app.route("/practise/<tt>", methods=["GET", "POST"])
def practise(tt):
    if not "username" in session:
        return redirect("/login")
    else:
        return render_template("practise.html", timestable = int(tt), username = session["username"], numbers = range(1,13))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("admin_username") == "bohemian" and request.form.get("admin_pw") == "I0AM&fr3e":
            
            # Getting all the data
            user_data = []
            with open("data/users.csv", "r", newline="") as usersfile:
                usersreader = csv.reader(usersfile, delimiter=" ")
                for row in usersreader:
                    user_data.append(row)

            medal_data = []
            with open("data/medals.csv", "r", newline="") as medalsfile:
                medalsreader = csv.reader(medalsfile, delimiter=" ")
                for row in medalsreader:
                    medal_data.append(row)

            return render_template("data.html", user_data = user_data, medal_data = medal_data)
        else:
            return render_template("admin.html")
    else:
        return render_template("admin.html")

if __name__ == "__main__":
    app.run()