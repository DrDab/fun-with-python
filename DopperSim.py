"""
DopplerSim

Description:
"""

import pygame
pygame.init()
import tsk
import math

w = pygame.display.set_mode([800, 800])
c = pygame.time.Clock()

px = 400.0
py = 400.0

v_sound = 343.0
v_player = 400.0

period = 1 / 20.0

timeRem = period

running = True

circles = []

while running:
    w.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    
    dt = c.get_time() / 1000.0
    timeRem -= dt
    if timeRem <= 0:
        timeRem = period
        circles.append([px, py, 0.0])
        
    for circle in circles:
        if circle[2] > 800:
            circles.remove(circle)
            continue
        circle[2] += v_sound * dt
        pygame.draw.circle(w, (241, 156, 187), (circle[0], circle[1]), int(circle[2]), 2)
    
    if tsk.get_key_pressed(pygame.K_w):
        py -= v_player * dt
    if tsk.get_key_pressed(pygame.K_s):
        py += v_player * dt
    if tsk.get_key_pressed(pygame.K_a):
        px -= v_player * dt
    if tsk.get_key_pressed(pygame.K_d):
        px += v_player * dt
        
    pygame.draw.circle(w, (255, 255, 255), (px, py), 5)
    
    c.tick(60)
    pygame.display.flip()
        
        
