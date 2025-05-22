from threading import Thread
from pygame import time
import time as t
import socket

clock = time.Clock()

health = 100
players = []
projectiles = []

data = []

_restart = False

sinceLastNetworkTick = 0

def send_data(string:str):
    try: s.send(string.encode())
    except: return False
    return True

def start(ip:str, port:int, name:str):
    Thread(target=_start_blocking, args=(ip, port, name),daemon=True).start()

def init():
    global clock, s, health, players, projectiles, data, _restart
    clock = time.Clock()

    health = 100
    players = []
    projectiles = []

    data = []

    _restart = False

def restart():
    global _restart
    _restart = True

def recvall(s:socket.socket):
    buf = bytes()
    while True:
        s.settimeout(0.001)

        try: a = s.recv(2048)
        except socket.timeout:
            break

        buf += a
    return buf

def _start_blocking(ip:str, port:int, name:str):
    global players, projectiles, data, old_data, health, s, _restart
    global sinceLastNetworkTick

    data = [name, '0', '0']

    s = socket.socket()

    t.sleep(0.1)
    s.connect((ip, port))
    t.sleep(0.1)
    s.send(name.encode())
    t.sleep(0.1)

    while not _restart:
        try:
            # Send our current position, velocity, ect
            s.send((','.join(data)+'\r').encode())

            # Server will respond with every other player's data
            s.settimeout(0.2)
            msg = recvall(s).decode()

            try: health, raw_players, raw_projectiles = msg.split('==')
            except: continue

            health      = int(health)
            players     = [player.split(',') for player in raw_players.split('|')]
            projectiles = raw_projectiles.split('|')

            sinceLastNetworkTick = 0

            clock.tick(20)

        except socket.timeout:
            print('Timed out')
            continue

        except Exception as e:
            print(e)
            raise e


    init()
    _start_blocking(ip,port,name)







