from threading import Thread
import time as t
import socket

s = socket.socket()

players = []
projectiles = []

data = []

def send_data(data:str):
    s.send(data.encode())

def start(ip:str, port:int, name:str):
    Thread(target=_start_blocking, args=(ip, port, name),daemon=True).start()

def _start_blocking(ip:str, port:int, name:str):
    global players, projectiles, data
    data = [name, '0', '0', '0', '0']

    s.connect((ip, port))
    t.sleep(0.1)
    s.send(name.encode())
    t.sleep(0.1)

    while True:
        try:
            # Send our current position, velocity, ect
            s.send(','.join(data).encode())

            # Server will respond with every other player's data
            s.settimeout(0.3)
            raw_players,raw_projectiles = s.recv(1024).decode().split('=')

            players     = [player.split(',') for player in raw_players.split('|')]
            projectiles = [proj.split(',') for proj in raw_projectiles.split('|')]
            

        except socket.timeout:
            continue

        except Exception as e:
            print(e)
            raise e
            break







