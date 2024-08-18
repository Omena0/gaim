from math import sin, cos, atan2, pi
from random import randrange
import MPLib as mplib
import pygame.gfxdraw
import numpy as np
import pygame
pygame.init()

size = (640, 480)

# Init pygame
disp = pygame.display.set_mode(size,pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)


pygame.mouse.set_cursor(pygame.cursors.broken_x)

# Init camera
centerX, centerY = size[0]//2, size[1]//2
cx, cy = 0, 0
px, py = centerX, centerY

# Init movement vars
pressed = []
velX = 0
velY = 0
accel = 55
airResistance = 1.13

# Init projectiles
projectiles:list[tuple[tuple[int,int], tuple[float, float], int]] = []

## Weapon stats ##

spread = 70
min_spread = 0.01
sight_range = 500

firerate = 1 # frames per round

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

name = 'TestPlayer'+ str(randrange(0,1000))

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
    if pygame.mouse.get_pressed()[0] and frame % firerate == 0:
        r = (end - start) * ((abs(mx-centerX) + abs(my-centerY))) / 2.2
        r = round(r)

        if r:
            rx = randrange(-r,r)
            ry = randrange(-r,r)
        else:
            rx,ry = 0,0

        vec = np.array([mx-centerX + rx, my-centerY + ry])
        vec = vec / np.linalg.norm(vec) * 100

        mplib.send_data(','.join(['SHOOT',str(-cx+centerX),str(-cy+centerY),str(vec[0]),str(vec[1]),'5']))



    ### RENDERING ###

    # Draw background
    disp.fill((0,0,0))

    # "map"
    draw_rect(0,0,size[0]*2,size[1]*2, (30,30,30))

    ## Draw accuracy ##

    radius = (abs(velX) + abs(velY)) / spread
    start  = atan2(centerX - mx,centerY - my) + pi/2 - radius/2
    end    = start + radius
    start -= min_spread
    end   += min_spread

    draw_sector((px, py), sight_range, start, end, (40,40,40))

    ## Draw player ##
    #pygame.draw.circle(disp, (70,70,70), (centerX,centerY), 20)

    for p in projectiles:
        pygame.draw.circle(disp, (255,255,255), (p[0][0]+cx, p[0][1]+cy), 5)

    # Draw players
    for p in mplib.players:
        p[1] = -float(p[1]) + centerX + cx
        p[2] = -float(p[2]) + centerY + cy
        p[3] = float(p[3])
        p[4] = float(p[4])

        if p[0] == name:
            px, py = int(p[1]), int(p[2])

        pygame.draw.circle(disp, (70,70,70), (p[1], p[2]), 20)

        text = font.render(p[0], True,(255,255,255))
        disp.blit(text, (p[1] - text.get_width()//2, p[2] - 30))


    data = [name, str(round(cx,2)), str(round(cy,2)), str(round(velX,2)), str(round(velY,2))]


    mplib.data = data

    pygame.display.update()
    dt = clock.tick(60) / 1000

    frame += 1


pygame.quit()