"""
LESSON: 3.6 - Time
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
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
# enemy = [posx, posy, health, velx, vely, speed]
enemies = []

playerx = 400
playery = 700
score = 0
current_wave = 0
time_left = 0.001
shirts_launched = 0
shirts_delivered = 0

running = False
wait = True
game_over = False

CANNON_SPEED = 20
ENEMY_SPEED = 5

font = pygame.freetype.SysFont('Arial', 12)
font.size = 20

c = pygame.time.Clock()
pygame.mouse.set_visible(False)

while wait:
    w.fill([255, 255, 255])
    font.render_to(w, (0, 0), "Use [A] and [D] keys to move. Press [SPACE] to launch a T-Shirt.")
    font.render_to(w, (0, 20), "Hold [SHIFT] to sprint.")
    font.render_to(w, ((SCREEN_WIDTH / 2) - 120, (SCREEN_HEIGHT / 2) - 20), "TRC T-Shirt Cannon Simulator")
    font.render_to(w, ((SCREEN_WIDTH / 2) - 120, (SCREEN_HEIGHT / 2)), ("Press [SPACE] to start."))
    font.render_to(w, ((SCREEN_WIDTH / 2) - 150, (SCREEN_HEIGHT / 2) + 60), ("Join us at www.titanrobotics.com"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            wait = False
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                wait = False
                running = True
                
    playerRekt = pygame.Rect(playerx - 10, playery - 10, 40, 40)
    pygame.draw.rect(w, (150, 150, 150), playerRekt)
    c.tick(60)
    pygame.display.flip()

while running:
    if len(enemies) == 0 and game_over == False:
        current_wave += 1
        time_left += 30
        t = 0
        while t < 3 * current_wave:
            enemies.append([random.randint(0, SCREEN_WIDTH), random.randint(0, 600), 1, random.random(), 0, 1])
            t += 1
            
    if time_left <= 0:
        game_over = True
    
    if game_over:
        projectiles = []
        enemies = []
        accuracy = 0.0
        try:
            accuracy = 100.0 * (shirts_delivered / shirts_launched)
        except Exception as e:
            accuracy = 0.0
        w.fill([255, 255, 255])
        font.render_to(w, ((SCREEN_WIDTH / 2) - 90, (SCREEN_HEIGHT / 2) - 20), "Great Job!")
        font.render_to(w, ((SCREEN_WIDTH / 2) - 90, (SCREEN_HEIGHT / 2)), ("T-Shirts delivered: %d" % score))
        font.render_to(w, ((SCREEN_WIDTH / 2) - 90, (SCREEN_HEIGHT / 2) + 20), ("Accuracy: %.2f%%" % accuracy))
        font.render_to(w, ((SCREEN_WIDTH / 2) - 180, (SCREEN_HEIGHT / 2) + 60), "You would make a great robot driver!")
        font.render_to(w, ((SCREEN_WIDTH / 2) - 180, (SCREEN_HEIGHT / 2) + 80), "Join our FRC team at: http://www.titanrobotics.com/join-frc")
    
    if game_over == False:
        w.fill([255, 255, 255])
        font.render_to(w, (0, 0), ("T-Shirts delivered: %d" % score))
        font.render_to(w, (0, 20), ("Wave: %d" % current_wave))
        font.render_to(w, (0, 40), ("Time left: %.3f" % time_left))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shirts_launched += 1
                projectiles.append([playerx, playery, 0, -1, CANNON_SPEED])
    
    if game_over == False:
        for projectile in projectiles:
            # integrate the projectile velocity to the projectile position
            projectile[0] += projectile[4] * projectile[2]
            projectile[1] += projectile[4] * projectile[3]
            
            # if a projectile leaves the screen, despawn it to save memory.
            if projectile[0] < 0 or projectile[0] > SCREEN_WIDTH or projectile[1] < 0 or projectile[1] > SCREEN_HEIGHT:
                projectiles.remove(projectile)
                continue
            
            # if a projectile hits an target, then do damage to the target
            # if the target's health is less than or equal to 0, despawn the defeated target
            projRemoved = False
            for enemy in enemies:
                enemy_dx = projectile[0] - enemy[0]
                enemy_dy = projectile[1] - enemy[1]
                if math.hypot(enemy_dx, enemy_dy) < 20:
                    shirts_delivered += 1
                    enemy[2] -= 1
                    if projRemoved == False:
                        projectiles.remove(projectile)
                        projRemoved = True
                if enemy[2] <= 0:
                    score += 1
                    enemies.remove(enemy)
            
            pygame.draw.circle(w, (0, 0, 0), (int(projectile[0]), int(projectile[1])), 2)
    
    if game_over == False:
        for enemy in enemies:
            # animate all enemies.
            enemy[0] += enemy[3]
            enemy[1] += enemy[4]
            if enemy[0] <= 0:
                enemy[3] *= -1
            if enemy[0] >= SCREEN_WIDTH:
                enemy[3] *= -1
            
            # draw enemies.
            pygame.draw.circle(w, (0, 0, 0), (int(enemy[0]), int(enemy[1])), 20)
            pygame.draw.circle(w, (255, 0, 0), (int(enemy[0]), int(enemy[1])), 10)
    
        # check if player is sprinting
        speedfactor = 1
        if tsk.get_key_pressed(pygame.K_RSHIFT) or tsk.get_key_pressed(pygame.K_LSHIFT):
            speedfactor = 2
        # check if player should be moved
        if tsk.get_key_pressed(pygame.K_a):
            if playerx >= 0:
                playerx -= 5 * speedfactor
        if tsk.get_key_pressed(pygame.K_d):
            if playerx <= SCREEN_WIDTH:
                playerx += 5 * speedfactor
            
        # draw the player
        playerRekt = pygame.Rect(playerx - 10, playery - 10, 40, 40)
        pygame.draw.rect(w, (150, 150, 150), playerRekt)
    
    # flip the display
    pygame.display.flip()
    c.tick(60)
    if game_over == False:
        time_left -= (c.get_time() / 1000)
    


# Turn in your Coding Exercise.
