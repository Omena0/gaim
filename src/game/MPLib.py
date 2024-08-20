from threading import Thread
from sys import getsizeof
from pygame import time
import time as t
import socket

clock = time.Clock()

s = socket.socket()

players = []
projectiles = []

data = []
old_data = []

def send_data(string:str):
    s.send(string.encode())

def start(ip:str, port:int, name:str):
    Thread(target=_start_blocking, args=(ip, port, name),daemon=True).start()

def recvall(s:socket.socket):
    do_recieve = True
    buf = bytes()
    while do_recieve:
        a = s.recv(256)
        if getsizeof(a) < 256:
            do_recieve = False
        buf += a
    return buf

def _start_blocking(ip:str, port:int, name:str):
    global players, projectiles, data, old_data
    data = [name, '0', '0']

    s.connect((ip, port))
    t.sleep(0.1)
    s.send(name.encode())
    t.sleep(0.1)

    while True:
        try:
            # Send our current position, velocity, ect
            s.send(','.join(data).encode())

            # Server will respond with every other player's data
            s.settimeout(0.1)
            msg = recvall(s).decode()

            raw_players,raw_projectiles = msg.split('==')

            players     = [player.split(',') for player in raw_players.split('|')]
            projectiles = raw_projectiles.split('|')

        except socket.timeout:
            continue

        except Exception as e:
            print(e)
            raise e
            break

        clock.tick(60)







