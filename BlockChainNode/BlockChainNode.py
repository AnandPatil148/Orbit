from BlockChain import *
from Node import Node
import json
import socket
import threading
import datetime
from uuid import uuid4

# Server Related Variables
encodeFormat = 'utf-8'
SERVER = ('127.0.0.1')
PORT = 6969

ADDR = (SERVER, PORT)

#Can be changed later
Node_User = 'Anand'

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[LISTENING] BlockChain Server is listening on {SERVER}:{PORT}...")

WebServers = []
NODES = []

Orbit = Blockchain()
#Orbit.create_room_genesis_block("Test", Node_User) commented for testing purposes
Orbit.load_chain("chain.json")



def commands():
    print("Commands Initiated")
    while True:
        cmd = input('')
        if cmd == '!VC':
            print( json.dumps(Orbit.to_dict(), indent= 4) )
        elif cmd ==  "!USERS":
            print(Orbit.users_count)
        elif cmd == '!stop':
            for server in WebServers:
                server.close()
            SystemExit(0)


# Function to handle SERVERS' connection
def HandleServer(SERVER: socket.socket, addr):
    while True:
        
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            dataString = SERVER.recv(1024).decode('utf-8')
            #print(f"{t}: {addr} -> {dataString}")
            
            # Sends message back to client
            
            if not dataString:
                raise socket.error("Disconnected")
            
            # Splitting Data String into Command & Arguments
            
            # GET Block from BlockChain 
            if dataString.startswith("GET"):
                blocktoget = dataString.split(" ")[1]
                roomname = dataString.split(" ")[3]
                
                data = Orbit.get_block(int(blocktoget), roomname) #Data of one Block in form of dict
                
                    
                # Send back the Data in JSON Formated string
                dataString = json.dumps(data) #convert to JSON Formated string
                SERVER.send(dataString.encode(encodeFormat)) #sends the data to the SERVER
                print(f"{t}: Data Sent To SERVER {addr}")
                continue
            
            elif dataString.startswith("AUTH"):
                sub_command = dataString.split(" ")[1]
                
                if sub_command == "REGISTER":
                    
                    auth_data = json.loads(dataString.split("!")[1]) #Getting the user credentials from message
                    
                    NAME = auth_data["NAME"]
                    EMAIL = auth_data["EMAIL"]
                    PASSWD = auth_data["PASSWD"]
                    
                    reg_usr = Orbit.register_user(NAME=NAME, EMAIL=EMAIL, PASSWD=PASSWD)
                    
                    if reg_usr:
                        response_data = json.dumps({
                            "ERROR": None
                        })
                        
                        SERVER.send(f"AUTH OK !{response_data}".encode())
                    
                
                    else:   # User already exists in the database
                        response_data = json.dumps({"ERROR":"User with this username or email already exists."})
                        SERVER.send(f"AUTH ERROR !{response_data}".encode())
                        
                        continue
                
                elif sub_command == "LOGIN":
                    
                    # User tries to login with username and password
                    auth_data = json.loads(dataString.split("!")[1]) #Getting the user credentials from message
                    NAME = auth_data["NAME"]
                    PASSWD = auth_data["PASSWD"]
                    
                    login_usr = Orbit.authenticate_user(NAME, PASSWD)
                    
                    if login_usr[0]:
                        response_data = json.dumps(login_usr[1])  # Return user info
                        SERVER.send(f"AUTH OK !{response_data}".encode())
                    
                    else:
                        if login_usr[1] == "INCORRECT PASSWORD":
                            response_data = json.dumps({
                            "ERROR": "Incorrect username or password.",
                            }) 
                            SERVER.send(f"AUTH ERROR !{response_data}".encode())
                        
                        else:
                            response_data = json.dumps({
                            "ERROR": "Account Not Found. Please Signup.",
                            }) 
                            SERVER.send(f"AUTH ERROR !{response_data}".encode())
                
                #need to be worked on
                elif sub_command == "EMAIL_UPDATE":
                    
                    # User tries to login with username and password
                    auth_data = json.loads(dataString.split("!")[1]) #Getting the new EMAIL credential from message
                    EMAIL = auth_data["EMAIL"]
                    NAME = auth_data["NAME"]
                    
                    if Orbit.update_user_data(NAME, new_email=EMAIL):
                        
                        response_data = json.dumps({
                            "ERROR": None
                        })
                        SERVER.send(f"AUTH OK !{response_data}".encode())
                        
                    else:
                        response_data = json.dumps({
                            "ERROR": "Failed to update email."
                        })
                        SERVER.send(f"AUTH ERROR !{response_data}".encode())
                
                elif sub_command == "PASSWD_UPDATE":
                    # Update the users password in the database
                    
                    auth_data = json.loads(dataString.split("!")[1]) #Getting the new Passwrod credentials from message
                    NAME = auth_data["NAME"]
                    OLD_PASSWD = auth_data["OLD_PASSWD"]
                    NEW_PASSWD = auth_data["NEW_PASSWD"]
                    
                    if not Orbit.authenticate_user(NAME, OLD_PASSWD):
                        response_data = json.dumps({
                            "ERROR":"Incorrect Old Password."
                        })
                        SERVER.send(f"AUTH ERROR !{response_data}".encode())
                        continue
                    
                    if Orbit.update_user_data(NAME, new_password=NEW_PASSWD):
                        
                        response_data = json.dumps({
                            "ERROR": None
                        })
                        SERVER.send(f"AUTH OK !{response_data}".encode())
                        
                    else:
                        response_data = json.dumps({
                            "ERROR": "Failed to update password."
                        })
                        SERVER.send(f"AUTH ERROR !{response_data}".encode())
                
                else:
                    response_data = {
                        'ERROR': 'Unknown command'
                    }
                    SERVER.send(f"AUTH ERROR !{json.dumps(response_data)}".encode())
            
            elif dataString.startswith("MINT"):
                #print(dataString)
                data = json.loads(dataString[5:]) #data is a disctionary here

                block = Block(
                    index=len(Orbit.chain), 
                    timestamp=data.get("TimeStamp"), 
                    data=data,
                    block_type="POST", 
                    mintedBy=Node_User
                    )
                Orbit.add_block(block, isRoomBlock=False)
                
            '''
            # Mintes a block on the Blockchain
            elif dataString.startswith("MINT"):
                block_data = dataString.split(" ")[1]
                data = json.loads(block_data) #data is a disctionary here

                block = Block(len(Orbit.chain), data.get("TimeStamp"), data)
                Orbit.add_block(block, roomBlockOrNot=False)
            '''
            
        except Exception as msg:
            print (f'{t}: {SERVER.getpeername()} has disconnected with msg {msg}')      
            WebServers.remove(SERVER)
            SERVER.close()
            break
    return

# Main function to receive the SERVER connections
def receive():
    while True:
        
        connSocket, address = server.accept()
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{t}: Connection is established with {str(address)}')
        try:
            
            connSocket.send("N or W".encode(encodeFormat)) # Sends N for Node and W for Webserver
            NorW = connSocket.recv(4096).decode(encodeFormat) # Waits for an ACK from the client
            
            if NorW == "N":
                NODES.append(connSocket)
                print(f'{t}: Server at {str(address)} is now connected as a node')
                Node_thread = threading.Thread(target=Node, args=(True, connSocket, address))
            elif NorW == "W":
                WebServers.append(connSocket)
                print(f'{t}: Server at {str(address)} is now connected as a web-client')
            
                WebServers.append(connSocket)
                WebServer_thread = threading.Thread(target=HandleServer, args=(connSocket, address), daemon=True)
                WebServer_thread.start()

            else:
                print("ERROR: Invalid connection type")
                connSocket.close()
                pass            
            
        except socket.error:
            print(f"{t}: {str(address)} DISCONNECTED WITH {address} WITH ERROR : {socket.error}")
            connSocket.close()
            pass



def startservers():
    cmd_thread = threading.Thread(target=commands)
    cmd_thread.start()
    
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()
    
startservers()


