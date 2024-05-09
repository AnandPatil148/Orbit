import socket
import json
import datetime
from BlockChain import *

# Function to handle Node connections
def node_handler(node_socket: socket.socket, addr:tuple, isOutgoing:bool, Orbit:Blockchain, encodeFormat:str, NODES:list):
    
    node_chain = []
    
    while True:
        
        try:
            
            if isOutgoing:
                query = "GET CHAIN" # Gets remote nodes BC info
                node_socket.send(query.encode(encodeFormat))
                
                node_response = node_socket.recv(4096).decode()
                
                if node_response.startswith("CHAIN"):
                    node_chain = json.loads(node_response[6:])
                    
                    if  len(node_chain) > len(Orbit.to_dict):
                        Orbit.set_chain(node_chain)
                        print(f"{addr} sent us a longer chain than ours so we have updated our chain")
                    else:
                        # send our chain to node
                        print(f"{addr} sent us a shorter chain but it didn't work")
            else:
                pass
            

            recvString = node_socket.recv(4096).decode()
            
            # If server closes connection or client sends QUIT message it will be caught here
            if not recvString:
                raise socket.error("Disconnected")
            
            if recvString == "GET CHAIN":
                query = "CHAIN " +json.dumps(Orbit.to_dict())
                node_socket.send(query.encode(encodeFormat))

            

        except Exception as e:
            print(f'Error in handling connection from {addr}: {e}') 
            node_socket.close()
            NODES.remove(node_socket)
            break
