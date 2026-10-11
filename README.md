# Orbit

Orbit is a blockchain-inspired real-time chat system built in Python. It combines a socket-based chat server, user authentication, room-based messaging, and a lightweight blockchain node that records chat activity as immutable blocks.

This project is not just a normal chat app — it follows a blockchain arc where messages and user data are treated as ledger entries, stored in a chain with hashes, timestamps, and room-based genesis blocks.

## Architecture

The project is divided into a few core parts:

- `ServerClient/server.py` - main chat server that handles client connections, auth, rooms, and message broadcasting
- `BlockChainNode/BlockChain.py` - blockchain logic, block creation, hashing, validation, and user registration flow
- `BlockChainNode/BlockChainNode.py` - node server that listens for peer/blockchain connections and maintains the blockchain network

## Core Concept

Orbit follows this flow:

1. A user connects to the chat server.
2. The server authenticates the user using a MySQL-backed login system.
3. The user joins or creates a chat room.
4. Messages are broadcast to users in that room.
5. The server sends the message payload to the blockchain node.
6. The blockchain node records the event as a block with metadata such as timestamp, room name, user ID, and message content.
7. The blockchain integrity is maintained using hashes and previous-hash chaining.

## Features

- Secure registration and login flow
- Password hashing with salt
- Room-based chat system
- MySQL persistence for login and room data
- Blockchain-backed message tracking
- Genesis blocks for rooms
- User wallet / identity tracking
- Peer node connection support

## Project Flow

The blockchain arc is designed like this:

- `GENESIS` block initializes the chain
- `ROOM_GENESIS` marks the start of a chat room
- `USER` blocks store user profile data and authentication information
- `POST`-style message blocks represent chat activity in a room

Each block contains:

- index
- timestamp
- block type
- data payload
- mintedBy
- previousHash
- hash

## Requirements

- Python 3.x
- MySQL server
- `mysql-connector-python`
- Python standard socket module

## Setup

1. Start the blockchain node:
   ```bash
   python BlockChainNode/BlockChainNode.py
   ```

2. Start the chat server:
   ```bash
   python ServerClient/server.py
   ```

3. Connect clients to the chat server using the client-side application in your project.

## Notes

This project is an experimental blockchain + chat prototype. It demonstrates how a messaging app can layer a verifiable ledger on top of a normal real-time communication system.

The blockchain layer is still evolving, and parts of the architecture are intended as a foundation for more advanced decentralized messaging features.

## Summary

Orbit is a Python blockchain-powered chat prototype that blends:

- real-time socket communication
- user authentication
- room management
- MySQL storage
- immutable blockchain event logging

It is an exploration of how chat systems can be extended into a trustable, auditable ledger model.
