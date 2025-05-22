import os
from threading import Thread
from time import sleep

def thing():
    os.system('py gaim.py')


for _ in range(100):
    Thread(target=thing).start()
    sleep(1)

