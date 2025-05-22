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
nameFont = pygame.font.SysFont(None, 20)
uiFont   = pygame.font.SysFont(None, 30)

pygame.mouse.set_cursor(pygame.cursors.broken_x)


# Camera
centerX, centerY = size[0]//2, size[1]//2
cx, cy = 0, 0
px, py = centerX, centerY

# Movement vars
pressed = []
velX = 0
velY = 0
speed = 3
accel = 13
airResistance = 10

## Weapon stats ##
accuracy = 100
min_spread = 0.02
sight_range = 500

fire_rate = 100 # ms
fire_timer = 0

mag_capacity = 300000
start_ammo = [30, 5]
ammo = start_ammo
reload_speed = 1000 # ms
reload_timer = 0

easing = 1

### Util ###
def floor(x, ndigits=0):
    if ndigits:
        return int(x*10**ndigits) / 10**ndigits
    else:
        return int(x)

def draw_rect(x,y,width,height,color,ui=False):
    if not ui:
        pygame.draw.rect(disp, color, (cx+x, cy+y, width, height))
    else:
        pygame.draw.rect(disp, color, (x, y, width, height))

def draw_sector(center, radius, theta0, theta1, color, ndiv=15):
    x0, y0 = center

    dtheta = (theta1 - theta0) / ndiv
    angles = [theta0 + i*dtheta for i in range(ndiv + 1)] 

    points = [(x0, y0)] + [(x0 + radius * cos(theta), y0 - radius * sin(theta)) for theta in angles]

    pygame.gfxdraw.filled_polygon(disp, points, color)

name = f'Player-{randrange(0,9999)}'

debug = False

#### MAINLOOP ####
mplib.start('127.0.0.1', 1337, name)

dt = 1
frame = 0
run = True
while run:
    mplib.sinceLastNetworkTick += 1
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
            try:
                if key == pygame.K_w:
                    pressed.remove('w')
                elif key == pygame.K_s:
                    pressed.remove('s')
                elif key == pygame.K_a:
                    pressed.remove('a')
                elif key == pygame.K_d:
                    pressed.remove('d')
            except: ...

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

    velX -= velX * dt * airResistance
    velY -= velY * dt * airResistance

    cx += velX * dt * 100 * speed
    cy += velY * dt * 100 * speed

    cx, cy = round(cx,3), round(cy,3)

    # SHOOTING
    fire_timer += dt*1000
    if reload_timer > 0:
        reload_timer -= dt*1000

    can_shoot = fire_timer > fire_rate and reload_timer <= 0
    if pygame.mouse.get_pressed()[0] and can_shoot:
        fire_timer = 0
        r = (end - start) * ((abs(mx-centerX) + abs(my-centerY))) / 2.2
        r = round(r)

        if r:
            rx = randrange(-r,r)
            ry = randrange(-r,r)
        else:
            rx,ry = 0,0

        vec = np.array([mx-px + rx, my-py + ry])
        vec = vec / np.linalg.norm(vec) * 5_000

        if ammo[0] <= 0:
            if ammo[1] > 0:
                ammo[1] -= 1
                print('Reloading...')
                ammo[0] = mag_capacity

                reload_timer = reload_speed

        else:
            ammo[0] -= 1
            mplib.send_data(f'SHOOT,{round(cx+px-centerX+velX)},{round(cy+py-centerY+velY)},{round(vec[0],2)},{round(vec[1],2)}\r')


    ### RENDERING ###

    # Draw background
    disp.fill((0,0,0))

    # "map"
    draw_rect(0,0,size[0]*2,size[1]*2, (30,30,30))

    # Offset player
    px = centerX - velX * speed * 5
    py = centerY - velY * speed * 5

    px, py = round(px,2), round(py,2)

    ## Draw accuracy ##

    radius = (abs(velX*10) + abs(velY*10)) / accuracy
    start  = atan2(px - mx, py - my) + pi/2 - radius/2
    end    = start + radius
    start -= min_spread
    end   += min_spread

    draw_sector((px, py), sight_range, start, end, (40,40,40))


    # Draw projectiles
    for p in mplib.projectiles:
        if not p: continue
        x,y,vx,vy = p.split(',')
        x,y = float(x),float(y)
        vx,vy = -float(vx), -float(vy)
        x += vx*mplib.sinceLastNetworkTick/easing
        y += vy*mplib.sinceLastNetworkTick/easing
        pygame.draw.circle(disp, (255,255,255), (-x+cx+centerX, -y+cy+centerY), 5)

    # Draw player
    pygame.draw.circle(disp, (70,70,70), (px, py), 20)
    pygame.gfxdraw.aacircle(disp, floor(px), floor(py), 19, (70,70,70))

    text = nameFont.render(name, True,(255,255,255))
    disp.blit(text, (px - text.get_width()//2, py - 30))

    # Draw players
    for p in mplib.players:
        if p[0] == name:
            continue

        try:
            x = -float(p[1]) + centerX + cx
            y = -float(p[2]) + centerY + cy
        except: continue

        pygame.draw.circle(disp, (71,72,73), (x, y), 20)

        text = nameFont.render(p[0], True, (255,255,255))
        disp.blit(text, (x - text.get_width()//2, y - 30))

    # Draw UI

    # Draw hp
    draw_rect(size[0]-200,size[1]-30,200,30, (20,20,20),ui=True)
    draw_rect(size[0]-200,size[1]-30,mplib.health*2,30, (70,70,70),ui=True)

    text = uiFont.render(f'HP: {mplib.health}%', True,(255,255,255))
    disp.blit(text, (size[0]-text.get_width()//2-100, size[1]-text.get_height()//2-15))

    # Draw ammo
    if sum(ammo) <= 0:
        text = 'OUT OF AMMO'
        width = 0

    elif reload_timer > 0:
        text = 'RELOADING'
        width = 200 - reload_timer / reload_speed * 200

    else:
        text = f'{ammo[0]} | {ammo[1]}'
        width = ammo[0]/mag_capacity*200

    draw_rect(size[0]-200,size[1]-60,200,30, (20,20,20),ui=True)
    draw_rect(size[0]-200,size[1]-60,width,30, (70,70,70),ui=True)

    text = uiFont.render(text, True, (255,255,255))
    disp.blit(text, (size[0]-text.get_width()//2-100, size[1]-text.get_height()//2-45))

    # Draw debug
    if debug:
        text = f'DEBUG | {cx=} {cy=}, {px=} {py=}'
        text = uiFont.render(text,True,(255,255,255))
        disp.blit(text,(0,0))

    # Check death
    if mplib.health <= 0:
        print('Bozo died')
        mplib.restart()

        # Camera
        centerX, centerY = size[0]//2, size[1]//2
        cx, cy = 0, 0
        px, py = centerX, centerY

        # Movement vars
        pressed = []
        velX = 0
        velY = 0

        # Shooting shit
        fire_timer = 0
        ammo = start_ammo
        reload_timer = 0

    # Update player state
    mplib.data = [name, str(round(cx)), str(round(cy))]

    pygame.display.update()
    dt = clock.tick(120) / 1000

    frame += 1


pygame.quit()