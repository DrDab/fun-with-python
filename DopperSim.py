"""
DopplerSim

Description:
"""

import pygame
import pygame.freetype
pygame.init()
import tsk
import math

fontDefault = pygame.freetype.SysFont('Arial', 12)
fontDefault.fgcolor = (255, 255, 255)
fontDefault.size = 15

w = pygame.display.set_mode([800, 800])
c = pygame.time.Clock()

px = 400.0
py = 400.0

v_sound = 340.0
v_player = 150.0

period = 1 / 10.0

timeRem = period

running = True

circles = []

while running:
    w.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                v_player += 10.0
            if event.key == pygame.K_DOWN:
                v_player -= 10.0
    
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
        pygame.draw.circle(w, (241, 156, 187), (int(circle[0]), int(circle[1])), int(circle[2]), 2)
    
    if tsk.get_key_pressed(pygame.K_w):
        py -= v_player * dt
    if tsk.get_key_pressed(pygame.K_s):
        py += v_player * dt
    if tsk.get_key_pressed(pygame.K_a):
        px -= v_player * dt
    if tsk.get_key_pressed(pygame.K_d):
        px += v_player * dt
        
    pygame.draw.circle(w, (255, 255, 255), (int(px), int(py)), 5)
    fontDefault.render_to(w, (0, 0), "Speed=%.2f m/s (Mach %.2f)" % (v_player, v_player / v_sound))
    
    c.tick(60)
    pygame.display.flip()
        
        
