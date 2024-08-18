from threading import Thread
from pygame import time
import socket

s = socket.socket()

s.bind(('127.0.0.1',1337))
s.listen(5)

clock = time.Clock()

players = {}
projectiles = []

def csHandler(cs:socket.socket,addr):
    try: name = cs.recv(1024).decode()
    except: return
    while True:
        try:
            cs.settimeout(0.3)
            data = cs.recv(1024).decode().split(',')

            if data[0] == 'SHOOT':
                projectiles.append([[float(data[1]), float(data[2])], [float(data[3]), float(data[4])], int(data[5])])
                continue

            players[name] = data

            p = '|'.join([','.join(v) for v in players.values()])
            
            proj = ''
            for projectile in projectiles:
                if proje

            allData = p + '=' + proj
            print(allData)

            cs.send(allData.encode())

        except socket.timeout:
            print('Timed out')

        except WindowsError as e:
            print(f'[-] {addr} [{e}]')
            players.pop(name)
            return

        except Exception as e:
            print(f'[-] {addr} [{e}]')
            players.pop(name)
            raise e
            return


frame = 0
def gameLoop():
    while True:
        for p in projectiles:
            p[0][0] += p[1][0]
            p[0][1] += p[1][1]

        print(len(projectiles))
        if frame % int((1000-len(projectiles))/100) == 0 and projectiles:
            projectiles.pop(0)
        
        clock.tick(60)
        frame += 1


while True:
    cs, addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler, args=(cs,addr),daemon=True).start()