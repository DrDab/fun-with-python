"""
HotlineMiami

Description:
"""
import tsk
import pygame
import pygame.freetype
import math
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

pygame.init()
w = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
w.fill([255, 255, 255])
# projectile = [posx, posy, velx, vely, speed]
projectiles = []
# enemy = [posx, posy, health, max health, speed]
enemies = []

playerx = 400
playery = 400
score = 0
current_wave = 0

running = True
wait = True

MUZZLE_VELOCITY = 20
ENEMY_SPEED = 5

font = pygame.freetype.SysFont('Arial', 12)
font.size = 20

pygame.mouse.set_visible(False)

while wait:
    w.fill([255, 255, 255])
    font.render_to(w, (0, 0), "Press W, A, S or D to start first wave.")
    font.render_to(w, (0, 20), "Use [W][A][S][D] keys to move, and the mouse to aim. Left-click to fire.")
    font.render_to(w, (0, 40), "Hold [SHIFT] to sprint. Use [1] and [2] to switch fire modes.")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            wait = False
            running = False
    if tsk.get_key_pressed(pygame.K_w) or tsk.get_key_pressed(pygame.K_s) or tsk.get_key_pressed(pygame.K_a) or tsk.get_key_pressed(pygame.K_d):
        wait = False

    for enemy in enemies:
        # draw enemies.
        r = 0
        g = 0
        half_health = enemy[3] / 2
        enemy_health = enemy[2]
        if enemy_health > half_health:
            g = 255 * ((enemy_health - half_health) / half_health)
        else:
            r = 255 * ((half_health - enemy_health) / half_health)
        pygame.draw.circle(w, (int(r), int(g), 0), (int(enemy[0]), int(enemy[1])), 20)

    pygame.draw.circle(w, (0, 0, 255), (int(playerx), int(playery)), 20)
    mousex, mousey = pygame.mouse.get_pos()
    # draw crosshair
    pygame.draw.line(w, (0, 0, 0), (mousex, mousey - 2), (mousex, mousey - 15), 3)
    pygame.draw.line(w, (0, 0, 0), (mousex, mousey + 2), (mousex, mousey + 15), 3)
    pygame.draw.line(w, (0, 0, 0), (mousex - 2, mousey), (mousex - 15, mousey), 3)
    pygame.draw.line(w, (0, 0, 0), (mousex + 2, mousey), (mousex + 15, mousey), 3)
    pygame.time.wait(50)
    pygame.display.flip()

fire_mode = 0 # 0 = automatic fire, 1 = spread fire
mode_strings = ["Auto", "Spread"]
shooting = False
while running:
    if len(enemies) == 0:
        current_wave += 1
        t = 0
        while t < 5 * current_wave:
            enemies.append([random.randint(playerx - 500, playerx - 400), random.randint(playery + 400, playery + 500), 10, 10, random.randint(1, 3)])
            t += 1
        b = 0
        while b < 5 * current_wave:
            enemies.append([random.randint(playerx + 400, playerx + 500), random.randint(playery - 500, playery - 400), 10, 10, random.randint(1, 3)])
            b += 1
    w.fill([255, 255, 255])
    font.render_to(w, (0, 0), "Wave " + str(current_wave))
    font.render_to(w, (0, 20), str(score) + " Neutralized")
    font.render_to(w, (0, 40), "Mode: " + mode_strings[fire_mode])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            if fire_mode == 0:
                shooting = True
            if fire_mode == 1:
                dyo = mousey - playery
                dxo = mousex - playerx
                theta = math.atan2(dyo, dxo)
                a1 = theta - (math.pi / 24.0)
                dy1 = math.sin(a1)
                dx1 = math.cos(a1)
                a2 = theta - (math.pi / 12.0)
                dy2 = math.sin(a2)
                dx2 = math.cos(a2)
                a3 = theta + (math.pi / 12.0)
                dy3 = math.sin(a3)
                dx3 = math.cos(a3)
                a4 = theta + (math.pi / 24.0)
                dy4 = math.sin(a4)
                dx4 = math.cos(a4)
                a5 = theta
                dy5 = math.sin(a5)
                dx5 = math.cos(a5)
                projectiles.append([playerx + dx1, playery + dy1, dx1, dy1, MUZZLE_VELOCITY])
                projectiles.append([playerx + dx2, playery + dy2, dx2, dy2, MUZZLE_VELOCITY])
                projectiles.append([playerx + dx3, playery + dy3, dx3, dy3, MUZZLE_VELOCITY])
                projectiles.append([playerx + dx4, playery + dy4, dx4, dy4, MUZZLE_VELOCITY])
                projectiles.append([playerx + dx5, playery + dy5, dx5, dy5, MUZZLE_VELOCITY])
        if event.type == pygame.MOUSEBUTTONUP:
            if fire_mode == 0:
                shooting = False
            
    mousex, mousey = pygame.mouse.get_pos()
    if shooting:
        # check the firing mode.
        if fire_mode == 0:
            # get unit vector components for projectile velocity
            dy = mousey - playery
            dx = mousex - playerx
            magnitude = math.hypot(dx, dy)
            dy /= magnitude
            dx /= magnitude
            
            # add a projectile to the list of projectiles.
            projectiles.append([playerx + dx, playery + dy, dx, dy, MUZZLE_VELOCITY])
     
    for projectile in projectiles:
        # integrate the projectile velocity to the projectile position
        projectile[0] += projectile[4] * projectile[2]
        projectile[1] += projectile[4] * projectile[3]
        
        # if a projectile leaves the screen, despawn it to save memory.
        if projectile[0] < 0 or projectile[0] > SCREEN_WIDTH or projectile[1] < 0 or projectile[1] > SCREEN_HEIGHT:
            projectiles.remove(projectile)
            continue
        
        # if a projectile collides with the player, end the game.
        #player_dx = projectile[0] - playerx
        #player_dy = projectile[1] - playery
        #if math.hypot(player_dx, player_dy) < 20:
        #    print("Game over. You got hit by a projectile.")
        #    running = False
        #    break
            
        # if a projectile hits an enemy, then do damage to the enemy.
        # if the enemy's health is less than or equal to 0, despawn the dead enemy.
        projRemoved = False
        for enemy in enemies:
            enemy_dx = projectile[0] - enemy[0]
            enemy_dy = projectile[1] - enemy[1]
            if math.hypot(enemy_dx, enemy_dy) < 20:
                enemy[2] -= 1
                if projRemoved == False:
                    projectiles.remove(projectile)
                    projRemoved = True
            if enemy[2] <= 0:
                score += 1
                enemies.remove(enemy)
        
        pygame.draw.circle(w, (0, 0, 0), (int(projectile[0]), int(projectile[1])), 2)
        
    for enemy in enemies:
        # have enemy chase the player.
        enemy_dx = playerx - enemy[0]
        enemy_dy = playery - enemy[1]
        enemy_distance_magnitude = math.hypot(enemy_dx, enemy_dy)
        if enemy_distance_magnitude < 20 * 2:
            print("Game over. You were eaten by a slime blob.")
            print("Total blobs neutralized: %d" % score)
            print("Waves survived: %d" % (current_wave - 1))
            running = False
            break
        enemy_dx /= enemy_distance_magnitude
        enemy_dy /= enemy_distance_magnitude
        enemy[0] += enemy_dx * enemy[4]
        enemy[1] += enemy_dy * enemy[4]
        
        # draw enemies.
        r = 0
        g = 0
        half_health = enemy[3] / 2
        enemy_health = enemy[2]
        if enemy_health > half_health:
            g = 255 * ((enemy_health - half_health) / half_health)
        else:
            r = 255 * ((half_health - enemy_health) / half_health)
        pygame.draw.circle(w, (int(r), int(g), 0), (int(enemy[0]), int(enemy[1])), 20)
    
    # check if player is sprinting
    speedfactor = 1
    if tsk.get_key_pressed(pygame.K_RSHIFT) or tsk.get_key_pressed(pygame.K_LSHIFT):
        speedfactor = 2
    
    if tsk.get_key_pressed(pygame.K_w):
        if playery >= 0:
            playery -= 5 * speedfactor
    if tsk.get_key_pressed(pygame.K_s):
        if playery <= SCREEN_HEIGHT:
            playery += 5 * speedfactor
    if tsk.get_key_pressed(pygame.K_a):
        if playerx >= 0:
            playerx -= 5 * speedfactor
    if tsk.get_key_pressed(pygame.K_d):
        if playerx <= SCREEN_WIDTH:
            playerx += 5 * speedfactor
    if tsk.get_key_pressed(pygame.K_1):
        fire_mode = 0
    if tsk.get_key_pressed(pygame.K_2):
        fire_mode = 1
    if tsk.get_key_pressed(pygame.K_3):
        fire_mode = 2
        
    # draw the player
    pygame.draw.circle(w, (0, 0, 255), (int(playerx), int(playery)), 20)
    
    # draw crosshair
    pygame.draw.line(w, (0, 0, 0), (mousex, mousey - 2), (mousex, mousey - 15), 3)
    pygame.draw.line(w, (0, 0, 0), (mousex, mousey + 2), (mousex, mousey + 15), 3)
    pygame.draw.line(w, (0, 0, 0), (mousex - 2, mousey), (mousex - 15, mousey), 3)
    pygame.draw.line(w, (0, 0, 0), (mousex + 2, mousey), (mousex + 15, mousey), 3)
    
    # flip the display
    pygame.display.flip()
    pygame.time.wait(10)
    
 
