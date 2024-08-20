from threading import Thread
from pygame import time
from math import sqrt
import socket

s = socket.socket()

s.bind(('127.0.0.1',1337))
s.listen(5)

clock = time.Clock()

players = {}
projectiles = []

def csHandler(cs:socket.socket,addr):
    try: name = cs.recv(2048).decode()
    except: return
    while True:
        try:
            data = cs.recv(2048).decode().split(',')

            if data[0] == 'SHOOT':
                projectiles.append([float(data[1]), float(data[2]), float(data[3]), float(data[4])])
                continue

            players[name] = data

            p = '|'.join([','.join(v) for v in players.values()])
            
            proj = ''
            _, x, y= players[name]
            x,y = float(x), float(y)
            for i,projectile in enumerate(projectiles):
                px,py,*_ = projectile

                proj += f'{round(px)},{round(py)}|'

            proj = proj.removesuffix('|')

            allData = p + '==' + proj

            cs.send(allData.encode())

        except socket.timeout:
            print('Timed out')

        except WindowsError as e:
            print(f'[-] {addr} [{e}]')
            players.pop(name)
            return

        except ValueError:
            ...

        except Exception as e:
            print(f'[-] {addr} [{e}]')
            players.pop(name)
            raise e
            return


frame = 0
def gameLoop():
    global frame
    dt = 1
    while True:
        for p in projectiles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt

            if abs(p[0]) + abs(p[1]) > 4000:
                projectiles.remove(p)

        if frame % round(100-len(projectiles)/1000) == 0 and projectiles:
            projectiles.pop(0)

        dt = clock.tick(120) / 1000
        frame += 1

Thread(target=gameLoop,daemon=True).start()

while True:
    cs, addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler, args=(cs,addr),daemon=True).start()