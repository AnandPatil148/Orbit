"""
A Node Class that represents the remote node and is run on a new thread when ever a node gets connected

"""

import json
import threading
import socket 


class Node(threading.Thread):
    def __init__(self, isRemote:bool, nodeSocket:socket.socket , addr=('127.0.0.1',9999)):
        self.localOrRemote = isRemote
        self.address = addr
        self.nodeSocket = nodeSocket
        
        # A lock to prevent multiple threads from accessing the same data at once
        self.lock = threading.Lock()
        threading.Thread.__init__(self)
        
    # Sync the local blockchain data to the  remote server's blockchain
    def sync_blockchain(self,local_bc,remote_bc):
        pass
            
            
    def connect(self,host='localhost',port=8080):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            print("Connected to Server")
            return True
        except Exception as e:
            print(f"Error Connecting to Server : {str(e)}")
            return False
    
    def send(self,data):
        try:
            self.sock.sendall(data.encode())
        except BrokenPipeError: 
            print("Connection lost")
            exit()
            
    def close(self):
        self.sock.close()
        
    def recv(self):
        data = self.sock.recv(4096).decode()
        return json.loads(data)
        