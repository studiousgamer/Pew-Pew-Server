import socket
from _thread import *
import sys
import random
import json
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
server_ip = socket.gethostbyname(server)
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
mappath = "server/map.json"

wallData = []
mapData = json.load(open(mappath))
x, y = 0, 0
for i in mapData:
    for k in i:
        if k == 1:
            wallData.append([x, y])
        x += 32
    x = 0
    y += 32

s.listen(10)
print("Waiting for a connection")

players = {}
bullets = {}


def movePlayer(x, y) -> bool:
    for mapx, mapy in wallData:
        if (
            x in range(mapx - 16, mapx + 32 + 16)
            and y in range(mapy - 16, mapy + 32 + 16)
            or x > 800 - 16
            or y > 600 + 16
            or x < 0 + 16
            or y < 0 + 16
        ):
            return False
    return True

def gen_spawn_coords() -> list[int]:
    x = random.randint(0, 800)
    y = random.randint(0, 600)
    while not movePlayer(x, y):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
    return [x, y]


def threaded_client(conn, addr):
    global players
    players[str(addr)] = {
        "name": addr,
        "id": addr,
        "pos": gen_spawn_coords(),
        "health": 100,
        "rotation": 0,
    }

    conn.send(str.encode(json.dumps(players[str(addr)])))
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = json.loads(reply)
                if reply["type"] == "update":
                    x, y = reply["payload"]["pos"]
                    if movePlayer(x, y):
                        players[str(addr)]["pos"] = [x, y]
                        players[str(addr)]["rotation"] = reply["payload"]["rotation"]
                    conn.send(str.encode(json.dumps(players[str(addr)])))

                elif reply["type"] == "get":
                    if reply["payload"] == "all":
                        conn.send(str.encode(json.dumps(players)))
                    elif reply["payload"] == "self":
                        conn.send(str.encode(json.dumps(players[str(addr)])))
                    elif reply["payload"] == "map":
                        conn.send(str.encode(json.dumps(mapData)))
                        
                elif reply["type"] == "move":
                    direction = reply["payload"]
                    x, y = players[str(addr)]["pos"]
                    if direction == "up":
                        y -= 5
                    elif direction == "down":
                        y += 5
                    elif direction == "left":
                        x -= 5
                    elif direction == "right":
                        x += 5
                    elif direction == "rot":
                        players[str(addr)]["rotation"] = reply["deg"]
                    if movePlayer(x, y):
                        players[str(addr)]["pos"] = [x, y]
                    conn.send(str.encode(json.dumps(players[str(addr)])))

                else:
                    print(f"Unknown command: {reply}")

        except Exception as e:
            print(e)
            break

    print("Connection Closed")
    conn.close()
    players.pop(str(addr))
    if str(addr) in bullets:
        bullets.pop(str(addr))


def main():
    while True:
        conn, addr = s.accept()
        print("Connected to: ", addr)
        start_new_thread(threaded_client, (conn, addr))


start_new_thread(main, ())
while True:
    pass
