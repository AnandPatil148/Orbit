#A Flask Based Web Client for Blockchain server
from flask import Flask, redirect, url_for, jsonify, request, render_template, session, flash
from flask_socketio import SocketIO
from datetime import timedelta
import Orbit_NodeAPI as API
import os
import json

#BCN_ip = '19.ip.gl.ply.gg'
#BCN_port = 28536

#BCN params
BCN_ip =  os.getenv('BCN_IP')
BCN_port = int(os.getenv('BCN_PORT'))

API.set_params(BCN_ip, BCN_port)

app = Flask(__name__)
#socketIO = SocketIO(app)

# Setup the secret key for sessions
app.secret_key = "yomamagay"

app.permanent_session_lifetime = timedelta(days=5)


@app.route("/")
def index():
    if "USERID" in session: #Checks if user is logged in
        return render_template("index.html"  , ROOMS = session["ROOMS"])
    
    else:
        return redirect(url_for("login"))
    
@app.route("/signup/", methods = ["POST", "GET"])
def signup():
    
    if request.method == "POST":
        
        NAME = request.form["NAME"]
        EMAIL = request.form["EMAIL"]
        PASSWD = request.form["PASSWD"]
        CPASSWD = request.form["CPASSWD"]
        
        if NAME == "" or EMAIL == "" or PASSWD == "":
            flash('Please fill out all fields!')
            return redirect(url_for('signup'))
            
        # Checks if passwords match
        elif PASSWD != CPASSWD:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))
            
                
        else:
            user_info = json.dumps({
                'NAME' : NAME,
                'EMAIL' : EMAIL,
                'PASSWD' : PASSWD
            })
            
            response = API.sign_up(user_info)   # Sign up with API
            
            if  response[0]:
                flash('Sign Up Successful! Please Log In Now')
                return redirect(url_for('login'))
            
            else:
                e = response[1]
                flash(str(e))
                return render_template("signup.html")
    
    else: #If Method is GET       
        return render_template('signup.html')  
    
@app.route("/login/", methods = ["POST", "GET"])
def login():
    
    if request.method == "POST":
        session.permanent = True
                
        NAME = request.form.get("NAME", "")
        #login thru email rather than username
        
        PASSWD = request.form.get("PASSWD", "")
        
        login_info = json.dumps({
            'NAME' : NAME,
            'PASSWD' : PASSWD
        })
        
        response = API.login(login_info)       # Login with API
        
        if response[0]:
            userInfo = response[1]
            session["USERID"] = userInfo["USERID"]   # Save USER ID in
            session["NAME"] = userInfo["NAME"]       # Save USER NAME in Session
            session["EMAIL"] = userInfo["EMAIL"]     # Save EMAIL ADDRESS in Session
            session["ROOMS"] = userInfo["ROOMS"]     # Save ROOMS in Session
            flash('Logged In!')
        
        else:
            flash("An error occurred while trying to log in.", "error")
            flash(response[1])

        return redirect(url_for("index"))      
     
    else: #If Method is GET
        if "USERID" in session:
            return redirect(url_for("index"))

        else:
            return render_template("login.html")

@app.route("/user/",methods = ["POST", "GET"])
def user():
    EMAIL = None
    
    if "USERID" in session:
        NAME = session["NAME"]
        
        if request.method == "POST":
            
            if "EMAIL" in request.form:
                EMAIL = request.form["EMAIL"]
                
                if EMAIL == session["EMAIL"]:
                    flash("Please enter a new email address.") 
                    return redirect(url_for("user"))
                                    
                email_info = json.dumps({
                    "NAME": NAME,
                    "EMAIL": EMAIL
                })
                
                response = API.email_update(email_info) 
                
                if response[0]:
                    session["EMAIL"] = EMAIL
                    flash("Email Updated Successfully", "info")
                    
                else:
                    flash("Failed to Update Email", "error")
                    flash(response[1])
                
                return redirect(url_for("user"))
            
            else:
                
                OLD_PASSWD = request.form["OLD_PASSWD"]
                NEW_PASSWD =  request.form["NEW_PASSWD"]
                
                passwd_info = json.dumps({
                    "NAME": NAME,
                    "OLD_PASSWD": OLD_PASSWD,
                    "NEW_PASSWD":NEW_PASSWD
                })
                
                response = API.passwd_update(passwd_info)
                
                if not response[0]:
                    flash(response[1])
                    
                else:
                    flash("Password Changed Successfully", "info")
        
                return redirect(url_for("user"))
        # If no changes were made just go back to the user page
            
        else:
            if "EMAIL" in session:
               EMAIL = session["EMAIL"]
                        
        return render_template("user.html", NAME = NAME, EMAIL = EMAIL, ROOMS = session["ROOMS"])
    
    else:
        return redirect(url_for("login"))
    
    
@app.route("/room/<roomname>")
def room(roomname):
    #check if user has logged in
    if "USERID" not in session:  
        return redirect(url_for('login'))  
    
    else:
        #Check if User can access room
        ROOMS = session["ROOMS"]
        if roomname not in ROOMS: 
            flash("You don't have permission to view this page."  , "warning")
            return redirect(url_for("index"))
      
        else:
            
            nOfBlocks = request.args.get("nOfBlocks")
            
            #checks if noOfBlocks is null or 0
            if nOfBlocks == None or nOfBlocks == 'None':
                nOfBlocks = 3
            else:
                try:
                    nOfBlocks = int(nOfBlocks)
                except:
                    flash("Invalid number of blocks entered.", "error")
                    return redirect(url_for("room", roomname=roomname))
            
            response = API.get_blocks(nOfBlocks, roomname)
            
            if response[0]:
                BlockData = response[1]
            
            else:
                BlockData = []
            
            return render_template("room.html", roomname = roomname, ROOMS = session["ROOMS"], nOfBlocks=nOfBlocks, data_list = BlockData)


@app.route("/room/<roomname>/newpost/" , methods=["GET", "POST"])
def newpost(roomname):
    
    #check if user has logged in
    if request.method == "POST":
        
        message = request.form.get("POSTMSG", "")
        
        #check if message if null or not 
        if message == "":
            flash("Message cannot be empty!","danger")
            return redirect(url_for("newpost", roomname = roomname))
        
        NAME = session["NAME"]
        UserID = session["USERID"]
        
        API.mint_blocks(UserID,NAME, message, roomname)
        
        return redirect(url_for("room", roomname = roomname))
        
    else:
       return render_template("newpost.html", ROOMS = session["ROOMS"])
    
@app.route("/logout/")
def logout():
    if "NAME" in session:
        NAME = session["NAME"]
        flash(f"{NAME} Successfully Logged Out", "info")
        
    session.pop("USERID", None)
    session.pop("NAME", None)
    session.pop("EMAIL", None)
    session.pop("ROOMS", None)
    return redirect(url_for("login"))



#socketIO.run(app=app, host='0.0.0.0', port=8080, debug=True)
#app.run(host = '0.0.0.0', port = 8080, debug = True)
#flask run --debug -h "0.0.0.0" -p 8080
