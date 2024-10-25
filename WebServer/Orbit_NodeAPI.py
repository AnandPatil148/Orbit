import datetime
import socket
import json
import time

def set_params(IP, port):
    global BCN_ip
    global BCN_port
    BCN_ip = IP
    BCN_port = port

def BCN_connect():
    '''
    Connects to the BCN server and returns a connected socket object. If it fails, raises an exception.
    '''
    BCN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Conn to Blockchain Nodes
    BCN.connect((BCN_ip, BCN_port))    # Connecting with local BCN Node (localhost:6969)
    
    NorW = BCN.recv(1024).decode()
    if NorW == "N or W":
        BCN.send("W".encode('utf-8'))   # Sending 'N' for Webserver
        time.sleep(1)
        
    return BCN    

def sign_up(user_info:dict):
    '''
    Params : {user_info = {
        "NAME" : str,
        "EMAIL" : str,
        "PASSWD" : str,
        }}
    Returns a dictionary with the response from server
    '''
    try:
                
        BCN = BCN_connect()  # TCP Conn to Blockchain Nodes

        BCN_query = f"AUTH REGISTER !{user_info}" # Sending Login Info to the server for Authentication
        BCN.send(BCN_query.encode("utf-8")) # Sends the Query

        dataString = BCN.recv(1024).decode() #  Receives Data from the Server and Decodes it into a String "AUTH 'response' !{data}"
                
        BCNAuthResponse = dataString.split(" ")[1] # Receives and Stores the Response from the BCN Node
                
        if BCNAuthResponse == "OK":
            return True, "OK"
                
        elif BCNAuthResponse == "ERROR":
            errorInfo = json.loads(dataString.split("!")[1])
            raise Exception (errorInfo["ERROR"])
                
        BCN.close()
                
    except Exception as e:
        print(e)
        #flash('Username Already Taken! Try Again With A Different Username')
        return False, str(e)


def login(login_info:dict):
    '''
    Params : login_info = {"USERID":"UserID","PASSWORD":"Password"}
    Returns : [bool,str] -> If Successful Returns [True,"Logged In"] else [False,"Error Message"]
    '''
    try:
        BCN = BCN_connect()  # TCP Conn to Blockchain Nodes
        
        BCN_query = f"AUTH LOGIN !{login_info}" # Sending Login Info to the server for Authentication
        BCN.send(BCN_query.encode('utf-8')) # Sends the Query
        
        dataString = BCN.recv(1024).decode() #  Receives Data from the Server and Decodes it into a String "AUTH 'response' !{data}"
        
        BCNAuthResponse = dataString.split(" ")[1] # Receives and Stores the Response from the BCN Node
        
        if BCNAuthResponse == "OK":
            userInfo = json.loads(dataString.split("!")[1])   # User Information received from BCN is in JSON format to Python Dictionary
            return True, userInfo
            
        elif BCNAuthResponse == "ERROR":
            errorInfo = json.loads(dataString.split("!")[1])
            raise Exception (errorInfo["ERROR"])
        
        else:
            print("Unexpected response from BCN")
        
        BCN.close()
        
    except Exception as e:
        print(e)
        return False, str(e)    


def email_update(email_info:dict):
    '''
    Updates User's Email in Database & sends a verification mail to new Email ID
    Params : email_info = {"NAME": NAME,"NEW_EMAIL":"NewEmail"}
    Returns : [Bool,Str] -> If Successful Returns [True,"Updated"] else [False,"Error Message"]
    '''
    try:
        BCN = BCN_connect()  # TCP Conn to Blockchain Nodes
        
        BCN_query = f"AUTH EMAIL_UPDATE !{email_info}" # Sending New Email Info to the server for Updating
        BCN.send(BCN_query.encode('utf-8')) # Sends the Query
        dataString = BCN.recv(1024).decode() #  Receives Data from the Server and Decodes it into a String "AUTH 'response' !{data}
        
        BCNAuthResponse = dataString.split(" ")[1] # Receives and Stores the Response from the BCN Node
        
        if BCNAuthResponse == "OK":
            return True, "OK"
                    
        elif BCNAuthResponse == "ERROR":
            errorInfo = json.loads(dataString.split("!")[1])
            raise Exception (errorInfo["ERROR"])
        
        BCN.close()
    
    except Exception as e:   # If connection fails it will return an error message
        return False, str(e)
    

def passwd_update(passwd_info:dict)->bool:
    """
    Updates user password on database
    Params :  passwd_info = {
                'NAME':'NAME',
                'OLD_PASSWD': 'Old Password',
                'NEW_PASSWD':'NewPassword'
              }
    Returns : [Bool,Str] -> If Successful Returns [True,"Updated"] else [False,"Error Message"]
    """
    try:
        BCN = BCN_connect()
        BCN_query = f"AUTH PASSWD_UPDATE !{passwd_info}" #  New Password is sent with '!' separator
        BCN.send(BCN_query.encode('utf-8')) # Sends the Query
        
        dataString = BCN.recv(1024).decode('utf-8') #  Receives Data from the Server and Decodes it into a String "AUTH 'response' !{data}
        
        BCNAuthResponse = dataString.split(" ")[1] # Receives and Stores the Response from the BCN Node
        
        if BCNAuthResponse == "OK":
            return True, "OK"

        elif BCNAuthResponse == "ERROR":
            errorInfo = json.loads(dataString.split("!")[1])
            raise Exception (errorInfo["ERROR"])
    
    except Exception as e:
        return False, str(e)
    
    finally:
        BCN.close()
        
def get_blocks(nOfBlocks, roomname):
    '''
    Gets all blocks present till now on the blockchain
    '''
    
    BCN = BCN_connect()
    
    BCNquery = f"GET {nOfBlocks} FROM {roomname}" # Query for getting data from the blockchain
    BCN.send(BCNquery.encode('utf-8')) # Sends the Query
    dataString = BCN.recv(4096).decode('utf-8') # Receive Data from BCN and decode it into utf-8 format
    
    Blocks = json.loads(dataString)       # Loads into List of Dictionaries
    
    if Blocks != []:
        BCN.close()
        return True, Blocks
        
    else:
        BCN.close()
        return False, []
    

def mint_blocks(USERID, NAME, MESSAGE, ROOMNAME):
        #Time at which Message was recceived by server
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # '2024-02-14 01:13:15'
        #Collect data in the form of Dictionary
        data = {
            'TimeStamp': t,  #TimeStamp of the message
            'RoomName': ROOMNAME,  # Room name from which the client chats from
            'UserID': USERID,  # User ID for tracking user activity
            'Name': NAME, # UserName for the user who is chatting
            'Message': MESSAGE, # Message to be sent by the user
        }


        dataString = json.dumps(data) #convert to json string

        print(f"{NAME}: MINT "+dataString)
        
        BCN = BCN_connect()   # Connecting with Server
        
        BCN.send(f"MINT {dataString}".encode('utf-8')) #send json string to blockchain server
        
        #print(f"{t}:{roomname} - {NAME}: {message}")
        
        BCN.close()