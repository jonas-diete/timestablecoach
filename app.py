from flask import Flask, redirect, render_template, request, session
import csv
import requests
import io
import os
from github import Github
app = Flask(__name__)

# Key for signing the cookies
app.secret_key = "xxxxx"

# Authentication key and directory to get data files from github (to save on)
# This is using a private git repository
github = Github(xxxxx)
repository = github.get_user().get_repo("timestable-coach-data")

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("accepted") == "yes":
            session["cookies"] = "yes"
        
        # --- Reading text file and creating a users dictionary with usernames and passwords ---
        users = {}
        # Getting file from GitHub
        file = repository.get_contents("users.txt")
        # Decoding file and iterating through it
        for row in file.decoded_content.decode().split("\n"):
            username_to_save = ""
            if row:     # This is checking if the row is "true", i.e. not empty
                # Saving every character in a new string until we get to a space (delimiter)
                for char in row:
                    if char != " ":
                        username_to_save += char
                    else:
                        break
                # Saving the new string as username and the rest of the row (minus the newline char) as the password
                users[username_to_save] = row[len(username_to_save) + 1:]

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
        users = []
        file = repository.get_contents("users.txt")
        for row in file.decoded_content.decode().split("\n"):
            if row:     # This is checking if the row is "true", i.e. not empty
                username_to_save = ""
                if row:     # This is checking if the row is "true", i.e. not empty
                    # Saving every character in a new string until we get to a space (delimiter)
                    for char in row:
                        if char != " ":
                            username_to_save += char
                        else:
                            break
                users.append(username_to_save)
        if new_username in users:
            return render_template("register.html", register_message = "Username exists already. Try again.")
        
        # Checking if terms and conditions have been agreed to
        elif request.form.get("agreement") != "agreed":
            return render_template("register.html", register_message = "Please accept the Terms and Conditions.")

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
            # Saving new username and password in text file on github
            # Getting previous file
            file = repository.get_contents("users.txt") 
            # Updating content
            updated_file = file.decoded_content.decode() + new_username + " " + new_pw1 + "\n"
            # Updating file on github
            f = repository.update_file(file.path, "Overwriting users.txt", updated_file, file.sha)

            # Adding entry in medals.txt for the new user
            # 0 = no medals, 1 = bronze, 2 = silver, 3 = gold
            # Arranged in order of timestables, starting with 2x
            file = repository.get_contents("medals.txt")
            updated_file = file.decoded_content.decode() + new_username + "00000000000\n"
            f = repository.update_file(file.path, "Overwriting medals.txt", updated_file, file.sha)

            # Adding data to learning.txt. Creating a line of correct answers 
            # for each timestable for the new user. Starting with 2x.
            file = repository.get_contents("learning.txt")
            updated_file = file.decoded_content.decode() + new_username + "\n"
            for i in range(11):
                updated_file += "000000000000\n"

            f = repository.update_file(file.path, "Overwriting learning.txt", updated_file, file.sha)

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
            # Getting medal-data from file saved on github and saving it in user_medals
            user_medals_str = ""
            file = repository.get_contents("medals.txt")
            for row in file.decoded_content.decode().split("\n"):
                # Searching for username and checking there is not a longer username which includes the current one
                if session["username"] in row and len(row) == len(session["username"]) + 11:
                    user_medals_str = row[len(session["username"]):]
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
                # Saving all medals from all users from file into all_medals dictionary
                all_medals = {}
                file = repository.get_contents("medals.txt")
                for row in file.decoded_content.decode().split("\n"):
                    medals_of_user = []
                    medals_of_user_str = row[len(row) - 11:]
                    for i in medals_of_user_str:
                        medals_of_user.append(i)
                    all_medals[row[:len(row) - 11]] = medals_of_user

                # Updating all_medals with the medal earned from current user and current timestable
                for user in all_medals:
                    # Checking if new medal is actually better than the old one
                    if user == session["username"] and all_medals[user][int(tt) - 2] < medal_earned:
                        all_medals[user][int(tt) - 2] = medal_earned

                # Overwriting whole content of text file with updated all_medals
                file = repository.get_contents("medals.txt")
                updated_file = ""
                for user in all_medals:
                    medals_of_user_str = ""
                    for medal in all_medals[user]:
                        medals_of_user_str += medal
                    updated_file += user + medals_of_user_str + "\n"
                repository.update_file(file.path, "Overwriting medals.txt", updated_file, file.sha)
            
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