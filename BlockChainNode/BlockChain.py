import datetime
import hashlib
import json
import secrets

class Block():
    
    def __init__(self,index:int, timestamp:str, block_type:str, data:dict, mintedBy:str):
        self.index = index
        self.timestamp = timestamp
        self.block_type = block_type
        self.data = data
        self.mintedBy = mintedBy
        self.previousHash = "0"
        # Calculate the hash of block
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        return hashlib.sha256( (str(self.index) + self.timestamp + json.dumps(self.data) + self.mintedBy + self.previousHash).encode("utf-8") ).hexdigest()
    
    def to_dict(self):
        return {
            "Index": self.index,
            "Timestamp": self.timestamp,
            "BlockType": self.block_type, 
            "Data": self.data,
            "MintedBy": self.mintedBy,
            "PreviousHash": self.previousHash,
            "Hash": self.hash
            }
        
    @staticmethod
    def to_block(b_dict):
        b = Block(
            index=b_dict["Index"],
            timestamp=b_dict["Timestamp"],
            block_type=b_dict["BlockType"],
            data=b_dict["Data"],
            mintedBy=b_dict["MintedBy"]
            )
        
        b.previousHash = b_dict["PreviousHash"]
        b.hash = b.calculate_hash()
        return b
    
class Blockchain():
    """A blockchain class that contains methods to manage a blockchain."""

    def __init__(self):
        """
        Initialize the blockchain with a genesis block.
        """
        #self.chain = [self.create_genesis_block()]
        self.chain = []
        self.users_count = 0
        self.posts_count = 0

        self.wallets = {}  # Dictionary to store wallet addresses and blockchain identities
    
    def get_chain_length(self):
        """Returns the length of the chain."""
        return len(self.chain)
    
    def create_genesis_block(self):
        """
        Create and add the genesis block of the blockchain to json file.
        """
        
        with open('chain.json', 'r+', encoding='utf-8') as f:
            
            file_data = json.load(f) # Load JSON data from file to variable `file_data`
            
            #If no data in file, create new Genesis Block
            genesisBlock = Block(
                index=0, 
                timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                block_type="GENESIS", 
                data = {
                    'TimeStamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  #TimeStamp of the message
                    'RoomName': 'Lobby',  # Room name from which the client chats from
                    'UserID': 'SERVER',  # User ID for tracking user activity
                    'Name': 'SERVER', # UserName for the user who is chatting
                    'Message': 'GenesisBlock' , # Message to be sent by the user
                    },
                mintedBy="SERVER"
                )
            
            file_data["Blocks"].append(genesisBlock.to_dict()) # Add genesis block to list in JSON file
            f.seek(0)
            json.dump(file_data, f, ensure_ascii=False, indent=4) # Save new data back into the JSON file
        
        return genesisBlock
    
    def create_room_genesis_block(self, roomname, mintedBy):
        roomStartBlock = Block(
            index=self.get_chain_length(), 
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            block_type="ROOM_GENESIS", 
            data = {
                'TimeStamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  #TimeStamp of the message
                'RoomName': f'{roomname}',  # Room name from which the client chats from
                'UserID': 'SERVER',  # User ID for tracking user activity
                'Name': 'SERVER', # UserName for the user who is chatting
                'Message': 'GenesisBlock' , # Message to be sent by the user
                },
            mintedBy=mintedBy
            )
        
        self.add_block(roomStartBlock, isRoomBlock=True)
        
        #To check whether to add room genesis block to database or not
        with open('chain.json', 'r+', encoding='utf-8') as f:
            
            file_data = json.load(f)
            
            #Check if room genesis block is present or not
            for i in range(self.get_chain_length()):
                try:
                    file_data["Blocks"][i]["Data"]["RoomName"]
                    t = (i, True)
                except:
                    t = (i, False)
                    pass
            
            if t[1]:
                print(f"This room, {roomname}, already has a Genesis Block.")
                return False
            else:
                print("No Room Found")

                file_data["Blocks"].append(roomStartBlock.to_dict())
                f.seek(0)
                json.dump(file_data, f, ensure_ascii=False, indent=4)
                return True

    def load_chain(self,filename):
        try:
            f = open(filename, "rb")
            data = json.load(f)
            chain = []
            
            if data["Blocks"] == []:
                self.create_genesis_block()
                f = open(filename, "rb")
                data = json.load(f)
            
            for b_dict in data["Blocks"]:
                
                b = Block.to_block(b_dict)
                
                if b.block_type=="USER":
                    self.users_count+=1
                else :
                    self.posts_count+=1
                    
                chain.append(b)
            
            self.chain = chain
                
        except FileNotFoundError:
            print("No existing blockchain found.")
                    
    def load_wallets(self, filename):
        """
        # Under Dev
        """
        try:
            with open(filename, 'r') as file:
                self.wallets = json.load(file)
        except FileNotFoundError:
            # File not found, initialize with an empty dictionary
            self.wallets = {}
    
    def get_latest_block(self):
        """
        Return the latest block in the blockchain.
        """
        return self.chain[len(self.chain) - 1]

    def add_block(self, newBlock: Block, isRoomBlock: bool=False):
        """
        Add a new block to the blockchain with the previous hash set to the
        hash of the latest block.
        """
        newBlock.previousHash = self.get_latest_block().hash
        newBlock.hash = newBlock.calculate_hash()
        self.chain.append(newBlock)
        
        #If not a room genesis block add to global chain data base
        if not isRoomBlock:
            with open('chain.json', 'r+', encoding='utf-8') as f:

                file_data = json.load(f)

                file_data["Blocks"].append(newBlock.to_dict())
                f.seek(0)
                json.dump(file_data, f, ensure_ascii=False, indent=4)

    #Hashes Password
    def hash_password(self,passwordToHash:str, salt:bytes=None):
        if salt is None:
            salt = secrets.token_bytes(16)  # Generate a random 16-byte salt

        # Combine the password and salt, then hash
        hashed_password = hashlib.sha256(passwordToHash.encode() + salt).hexdigest()

        return hashed_password, salt

    # Verifies password
    def check_password(self,passwordToCheck, storedHashOfPassword, storedSalt):
        # Use the same process to hash the given password,
        # and compare it with the stored password
        generated_new_hash = self.hash_password(passwordToCheck, storedSalt)[0]
        return generated_new_hash == storedHashOfPassword
    
    def calculate_user_address(self, NAME, EMAIL, SALT):
        # Concatenate user attributes
        user_info = f"{NAME}{EMAIL}{SALT}"

        # Hash the concatenated string using SHA-256
        hashed_address = hashlib.sha256(user_info.encode()).hexdigest()

        return hashed_address

    def register_user(self, NAME:str, EMAIL:str, PASSWD:str,):
        
        for block in self.chain:
            if block.block_type == "USERS" and block.data["NAME"] == NAME:
                return False
        
        HASHED_PASSWD, SALT =  self.hash_password(PASSWD)
        self.users_count += 1
        
        # Create user authentication data
        user_data = {
            "USERID": self.users_count,
            "NAME": NAME,
            "EMAIL": EMAIL,
            "ADDRESS": self.calculate_user_address(NAME,EMAIL,SALT),
            "BALANCE": 0,
            "HASHED_PASSWD": HASHED_PASSWD,
            "SALT": SALT.hex(),
            "ROOMS": '["Lobby"]'
        }
        
        # Create a new block with user authentication data
        new_block = Block(
            index=self.get_chain_length(),
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            block_type="USER",
            data=user_data,
            mintedBy="SERVER"
        )
        
        # Add the new block to the blockchain
        self.add_block(new_block)
        
        return True
    
    def authenticate_user(self, NAME: str, PASSWD: str):
        """
        Find the latest block containing user authentication data
        """
        for block in reversed(self.chain):
            
            if block.block_type == "USER" and block.data["NAME"] == NAME:
                
                stored_PASSWD = block.data["HASHED_PASSWD"]
                stored_SALT = block.data["SALT"]
                
                # Decrypt password from hexadecimal format to bytes
                SALT_bytes = bytes.fromhex(stored_SALT)
                
                if self.check_password(PASSWD, stored_PASSWD, SALT_bytes):
                    response_data = {
                            "USERID": block.data["USERID"],
                            "NAME": block.data["NAME"],
                            "EMAIL": block.data["EMAIL"],
                            "ROOMS": json.loads(block.data["ROOMS"]),
                            }
                    return True, response_data
                
                else:
                    return False, "INCORRECT PASSWORD"
            
        return False, "Account Not Found. Please Signup."

    def update_user_data(self, NAME, new_password=None, new_email=None):
        """
        # Under Dev
        Update fields of interest (Password or Email). 
        If no changes are made just return the current data.
        """
        for block in reversed(self.chain):
            if block.block_type == "USER" and block.data["NAME"] == NAME:
                
                # Create a new block with the updated user information
                updated_data = block.data.copy()  # Create a copy of the existing data
                
                # Update user data if new password, email, or address is provided
                if new_password:
                    HASHED_PASSWD, SALT = self.hash_password(new_password, bytes.fromhex(updated_data["SALT"]))
                    updated_data["HASHED_PASSWD"] = HASHED_PASSWD
                
                if new_email:
                    updated_data["EMAIL"] = new_email
                    updated_data["ADDRESS"] = self.calculate_user_address(updated_data["NAME"], new_email, updated_data["SALT"])
                
                # Create a new block with the updated user data
                new_block = Block(
                    index=self.get_chain_length(),
                    timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    block_type="USER",
                    data=updated_data,
                    mintedBy="SERVER"
                )
                
                # Add the new block to the blockchain
                self.add_block(new_block)
                
                return True  # User data updated successfully
    
        return False  # User not found or data not updated
    
    #Future Idea
    '''
    def add_room_to_profile(self, email: str, room: str) -> None:
        """Add a room to a user's profile."""
        user_index = self._find_email_in_chain(email)
        if user_index is not None:
            user_block = self.get_block(user_index)
    '''
       
    def to_dict(self) -> list:
        """
        Convert the blockchain into a list of dictionaries for each block.
        """
        chainInfo = []
        for block in self.chain:
            chainInfo.append(block.to_dict())
        return chainInfo

    def is_chain_valid(self):
        """
        Validate the integrity of the blockchain by checking the hash and
        previous hash of each block.
        """
        i = 1
        while (i < len(self.chain)):
            currentBlock = self.chain[i]
            previousBlock = self.chain[i - 1]

            # Check if the current block's hash is equal to its calculated hash
            if (currentBlock.hash != currentBlock.calculate_hash()):
                return False

            # Check if the previous hash of the current block is equal to the hash
            # of the previous block
            if (currentBlock.previousHash != previousBlock.hash):
                return False

            i += 1
        
        return True
    
    def get_blocks(self, nOfBlock, roomname) -> list:
        blocksList = []
        
        for  block in reversed(self.chain):
            if len(blocksList) == nOfBlock: # If we have reached the desired number of blocks, stop iterating through the chain
                break
            
            elif block.block_type == "GENESIS" or block.block_type == "POST":
                if block.data["RoomName"] == roomname:
                    blocksList.append(block.to_dict())
                pass
        
        return blocksList
    
    def save_data(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.wallets, file)

    def register_wallet(self, wallet_address, blockchain_identity):
        # Register a new wallet address with its associated blockchain identity
        self.wallets[wallet_address] = blockchain_identity
        self.save_data('wallets.json')

    def get_blockchain_identity(self, wallet_address):
        # Retrieve the blockchain identity associated with a wallet address
        return self.wallets.get(wallet_address)

    def set_chain(self, chain:dict):
        """
        Sets the chain attribute of Blockchain class with the given dictionary.
        This method should be used only when loading an existing blockchain from disk.
        :param chain: A dictionary containing all the information about the blockchain.
        """
        bc = Blockchain()
        bc.chain = [Block.to_block(b) for b in chain]
        self.chain = bc.chain
 
"""
GCoin = Blockchain()
GCoin.addBlock(Block(len(GCoin.chain), "02/01/2024", {"amount" : 4}))
GCoin.addBlock(Block(len(GCoin.chain), "03/01/2024", {"amount" : 10}))

print(f"Is BlockChain Valid: {GCoin.isChainValid()}")

GCoin.chain[2].data = {"amount" : 100000}

print(f"Is BlockChain Valid: {GCoin.isChainValid()}")
        
print( json.dumps(GCoin.to_dict(), indent= 4) )
"""       