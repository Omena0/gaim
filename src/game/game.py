from math import sin, cos, atan2, pi
from random import randrange
import MPLib as mplib
import pygame.gfxdraw
import numpy as np
import time as t
import pygame
pygame.init()

size = (640, 480)

# Init pygame
disp = pygame.display.set_mode(size,pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

pygame.mouse.set_cursor(pygame.cursors.broken_x)


# Camera
centerX, centerY = size[0]//2, size[1]//2
cx, cy = 0, 0
px, py = centerX, centerY

# Movement vars
pressed = []
velX = 0
velY = 0
accel = 55
airResistance = 1.13

# Player stats
health = 100

## Weapon stats ##
spread = 60
min_spread = 0.02
sight_range = 500

firerate = 1 # ms per fire
timer = 0

### Util ###
def floor(x, ndigits):
    return int(x*10**ndigits) / 10**ndigits

def draw_rect(x,y,width,height,color):
    pygame.draw.rect(disp, color, (cx+x, cy+y, width, height))

def draw_sector(center, radius, theta0, theta1, color, ndiv=50):
    x0, y0 = center

    dtheta = (theta1 - theta0) / ndiv
    angles = [theta0 + i*dtheta for i in range(ndiv + 1)] 

    points = [(x0, y0)] + [(x0 + radius * cos(theta), y0 - radius * sin(theta)) for theta in angles]

    pygame.gfxdraw.filled_polygon(disp, points, color)

name = f'TestPlayer-{str(randrange(0, 1000))}'

#### MAINLOOP ####
mplib.start('127.0.0.1', 1337, name)

dt = 1
frame = 0
run = True
while run:
    mx, my = pygame.mouse.get_pos()

    pygame.display.set_caption(f'GAIM | FPS: {round(clock.get_fps(),2)}')

    ### Events ###
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        if event.type == pygame.VIDEORESIZE:
            size = event.size
            disp = pygame.display.set_mode(size,pygame.RESIZABLE)
            centerX, centerY = size[0]//2, size[1]//2

        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_w:
                pressed.append('w')
            elif key == pygame.K_s:
                pressed.append('s')
            elif key == pygame.K_a:
                pressed.append('a')
            elif key == pygame.K_d:
                pressed.append('d')

        elif event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_w:
                pressed.remove('w')
            elif key == pygame.K_s:
                pressed.remove('s')
            elif key == pygame.K_a:
                pressed.remove('a')
            elif key == pygame.K_d:
                pressed.remove('d')

    ## MOVEMENT ##
    if pressed:
        if 'w' in pressed:
            velY += accel * dt

        if 's' in pressed:
            velY -= accel * dt

        if 'a' in pressed:
            velX += accel * dt

        if 'd' in pressed:
            velX -= accel * dt

    velX = floor(velX / airResistance, 2)
    velY = floor(velY / airResistance, 2)

    cx += velX
    cy += velY

    # SHOOTING
    timer += dt*1000
    if pygame.mouse.get_pressed()[0] and timer > firerate:
        timer = 0
        r = (end - start) * ((abs(mx-centerX) + abs(my-centerY))) / 2.2
        r = round(r)

        if r:
            rx = randrange(-r,r)
            ry = randrange(-r,r)
        else:
            rx,ry = 0,0

        vec = np.array([mx-centerX + rx, my-centerY + ry])
        vec = vec / np.linalg.norm(vec) * 10_000

        mplib.send_data(f'SHOOT,{round(cx)},{round(cy)},{round(vec[0],2)},{round(vec[1],2)}\r')


    ### RENDERING ###

    # Draw background
    disp.fill((0,0,0))

    # "map"
    draw_rect(0,0,size[0]*2,size[1]*2, (30,30,30))

    # Offset player
    px = centerX + velX*2
    py = centerY + velY*2

    ## Draw accuracy ##

    radius = (abs(velX) + abs(velY)) / spread
    start  = atan2(px - mx, py - my) + pi/2 - radius/2
    end    = start + radius
    start -= min_spread
    end   += min_spread

    draw_sector((px, py), sight_range, start, end, (40,40,40))


    # Draw projectiles
    for p in mplib.projectiles:
        if not p: continue
        x,y = p.split(',')
        pygame.draw.circle(disp, (255,255,255), (-float(x)+cx+centerX, -float(y)+cy+centerY), 5)

    # Draw player

    pygame.draw.circle(disp, (70,70,70), (px, py), 20)

    text = font.render(name, True,(255,255,255))
    disp.blit(text, (px - text.get_width()//2, py - 30))

    # Draw players
    for p in mplib.players:
        if p[0] == name:
            continue

        try:
            x = -float(p[1]) + centerX + cx
            y = -float(p[2]) + centerY + cy
        except: continue

        pygame.draw.circle(disp, (70,70,70), (x, y), 20)

        text = font.render(p[0], True,(255,255,255))
        disp.blit(text, (x - text.get_width()//2, y - 30))

    mplib.data = [name, str(round(cx)), str(round(cy))]

    pygame.display.update()
    dt = clock.tick(60) / 1000

    frame += 1


pygame.quit()