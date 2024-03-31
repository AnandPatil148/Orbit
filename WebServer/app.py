#A Flask Based Web Client for Blockchain server
from flask import Flask, redirect, url_for, jsonify, request, render_template, session, flash
from flask_socketio import SocketIO
from datetime import timedelta
import datetime
import secrets
import socket
import json
import Orbit_API as API


app = Flask(__name__)
#socketIO = SocketIO(app)

#BCN params
BCN_ip = '180.ip.ply.gg'
BCN_port = 12378

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
            
        # Checks if passwords match
        elif PASSWD != CPASSWD:
            flash('Passwords do not match!')
            
                
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
        USERID = session["USERID"]
        NAME = session["NAME"]
        
        if request.method == "POST":
            EMAIL = request.form["EMAIL"]
            session["EMAIL"] = EMAIL
            
            email_info = json.dumps({
                "USERID": USERID,
                "EMAIL": EMAIL
            })
            
            response = API.email_update(email_info) 
            
            if response[0]:
                session["EMAIL"] = EMAIL
                flash("Email Updated Successfully", "info")
                
            else:
                flash("Failed to Update Email", "error")
                flash(response[1])
                
            return redirect(url_for("profile"))
            
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
            return redirect(url_for("room", roomname = roomname))
            
        
        #Time at which Message was recceived by server
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # '2024-02-14 01:13:15'
        NAME = session["NAME"]
        UserID = session["USERID"]
        
        #Collect data in the form of Dictionary
        data = {
            'TimeStamp': t,  #TimeStamp of the message
            'RoomName': roomname,  # Room name from which the client chats from
            'UserID': UserID,  # User ID for tracking user activity
            'Name': NAME, # UserName for the user who is chatting
            'Message': message, # Message to be sent by the user
        }


        dataString = json.dumps(data) #convert to json string

        print(f"MINT "+dataString)
        
        BCN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Conn to Blockchain servers
        BCN.connect((BCN_ip, BCN_port))    # Connecting with local BCN Node (localhost:6969)
        
        BCN.send(dataString.encode('utf-8')) #send json string to blockchain server
        
        #print(f"{t}:{roomname} - {NAME}: {message}")
        
        BCN.close()
        
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

