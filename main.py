import socket
from _thread import *
import sys
from player import Player
import random

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = 'localhost'
port = 5555
server_ip = socket.gethostbyname(server)
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))



s.listen(10)
print("Waiting for a connection")

players = {}

def threaded_client(conn, addr):
    global players
    players[str(addr)] = f"name:{addr}||id:{addr}||x:{random.randint(0, 800)}||y:{random.randint(0, 600)}||health:100||rotation:0"
    conn.send(str.encode(players[str(addr)]))
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = reply.split('||')
                if reply[0].split(':')[1] == 'get':
                    conn.send(str.encode(players[str(addr)]))
                    
                elif reply[0].split(':')[1] == 'update':
                    players[str(addr)] = reply[1]
                    
                elif reply[0].split(':')[1] == 'get_all':
                    conn.send(str.encode(str(players)))
            # conn.sendall(str.encode(str(reply)))
        except Exception as e:
            print(e)
            break
    
    print("Connection Closed")
    conn.close()
    players.pop(str(addr))
    
while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn, addr))