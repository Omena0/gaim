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
    try: name = cs.recv(2048).decode()
    except: return
    while True:
        try:
            data = cs.recv(2048).decode().split('\r')[0].split(',')

            if data[0] == 'SHOOT':
                projectiles.append([float(data[1]), float(data[2]), float(data[3]), float(data[4])])
                continue

            players[name] = data

            p = '|'.join([','.join(v) for v in players.values()])

            proj = ''
            _, x, y= players[name]
            x,y = float(x), float(y)
            for projectile in projectiles:
                px,py,*_ = projectile

                proj += f'{round(px)},{round(py)}|'

            proj = proj.removesuffix('|')

            allData = f'{p}=={proj}'

            cs.send(allData.encode())

        except socket.timeout:
            print('Timed out')

        except WindowsError as e:
            print(f'[-] {addr} [{e}]')
            players.pop(name)
            return

        except ValueError as e:
            print(e)
            try: cs.send('')
            except: break

        except Exception as e:
            print(f'[-] {addr} [{e}]')
            players.pop(name)
            if debug: raise e
            else: return


frame = 0
def gameLoop():
    global frame
    dt = 1
    while True:
        for p in projectiles:
            p[0] -= p[2] * dt / 2
            p[1] -= p[3] * dt / 2
            didHit = False
            for _ in range(int(max(3,10-(5-clock.get_fps()/120*5)))):
                try:
                    p[0] -= p[2] * dt / 10
                    p[1] -= p[3] * dt / 10
                    x,y,*_ = p
                    x,y = int(x),int(y)

                    for player in players.items():
                        name, px, py = player[1]
                        px, py = int(px), int(py)
                        if x in range(px-10,px+10) and y in range(py-10,py+10):
                            print(f'{name} was hit!')
                            projectiles.remove(p)
                            didHit = True
                            break

                except Exception as e: print(e)

            if didHit:
                break

            if abs(p[0]) + abs(p[1]) > 5000:
                projectiles.remove(p)

        if frame % round(100-len(projectiles)/1000) == 0 and projectiles:
            projectiles.pop(0)

        dt = clock.tick(120) / 1000
        print(f'TPS: {round(clock.get_fps(),2)} MSPT: {dt*1000}',end='       \r')
        frame += 1

Thread(target=gameLoop,daemon=True).start()

debug = True

while True:
    cs, addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler, args=(cs,addr),daemon=True).start()