from BlockChain import *
from web_server_handler import *
from node_handler import *
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
node_identifier = uuid4().hex

# List of all available nodes in the network. Later read and update from json file
NodesAddrList = [ ('127.0.0.1', 6969),
             ]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[LISTENING] BlockChain Server is listening on {SERVER}:{PORT} ...")

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
            
        elif cmd == "!NC":
            NodesConnect()
            
        elif cmd == "!NID":
            print( f"Your ID : {node_identifier}")
            
        elif cmd ==  "!USERS":
            print(Orbit.users_count)
            
        elif cmd == '!stop':
            for server in WebServers:
                server.close()
            SystemExit(0)


# Main function to receive the SERVER connections
def receive():
    
    print("Starting receiveing thread")
    
    while True:
        
        connSocket, address = server.accept()
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{t}: Connection is established with {str(address)}')
        try:
            
            connSocket.send("N or W".encode(encodeFormat)) # Sends N for Node and W for Webserver
            NorW = connSocket.recv(1024).decode(encodeFormat) # Waits for an ACK from the client
            
            if NorW == "N":
                
                connSocket.send("NID?".encode(encodeFormat)) # Asks for node identifier
                node_id = connSocket.recv(1024).decode()
                
                node_agrs = (connSocket, address, False, Orbit, encodeFormat, NODES)
                node_thread = threading.Thread(target=node_handler, args=node_agrs,  daemon=True, name=node_id)
                node_thread.start()

                NODES.append(connSocket)
                print(f'{t}: Server at {str(address)} is now connected as a node')
                
            elif NorW == "W":
            
                WebServers.append(connSocket)
                WebServer_thread = threading.Thread(target=web_server_handler, args=(connSocket, address, Orbit, encodeFormat, Node_User, WebServers), daemon=True)
                WebServer_thread.start()

                print(f'{t}: Server at {str(address)} is now connected as a web-client')
            else:
                print("ERROR: Invalid connection type")
                connSocket.close()
                pass            
            
        except Exception as e:
            print(f"{t}: {str(address)} DISCONNECTED WITH {address} WITH ERROR : {e}")
            connSocket.close()
            pass

def NodesConnect(): 
    
    for nodeAddr in NodesAddrList:
        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_socket.connect(nodeAddr)
        
        NorW = node_socket.recv(1024).decode()  # Receives the ACK from the a node
        
        if NorW == "N or W":
            node_socket.send("N".encode(encodeFormat))   # Tells the node that we are also a node
            
            node_socket.recv(1024).decode() # receives the NID? Msg
            node_socket.send(node_identifier.encode()) # sends NID
            
            node_socket.send("NID?".encode(encodeFormat)) # Asks for NID
            RNID = node_socket.recv(1024).decode()
            
            node_args = (node_socket, nodeAddr, True, Orbit, encodeFormat, NODES)
            node_thread = threading.Thread(target=node_handler, args=node_args, daemon=True, name=RNID)
            node_thread.start()
            
            NODES.append(node_socket)                     # Adds it to our list of nodes
            
            print("Connected to additional node.")
            
            return
        else:
            NODES.remove(node_socket)                     # Removes the disconnected node from our list
            print(f"Removed node {nodeAddr[0]}, reason: Disconnection")
            return

def startservers():
    cmd_thread = threading.Thread(target=commands)
    cmd_thread.start()
    
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()
    receive_thread.join()
    
    #node_connect_thread =  threading.Thread(target=NodeConnect, daemon=True)
    #node_connect_thread.start()
    #NodesConnect()
    
startservers()


