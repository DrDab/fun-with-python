"""
LESSON: 4.1 - Lists
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
"""

import math
import pygame
pygame.init()
import tsk

playerx = 5.0
playery = 3.0
player_rotation = 0.0
player_fov = 75.0 * math.pi / 180.0
player_rot_speed = 60 * math.pi / 180.0 # radians/sec
player_move_speed = 1.0 # units/sec
flashlightOn = False

player_prev_x = playerx
player_prev_y = playery
player_prev_rot = player_rotation

num_rects = 100
screen_height = 400
screen_width = 600
w = pygame.display.set_mode([screen_width, screen_height])
c = pygame.time.Clock()

gmp = [[1, 1, 1, 0, 1, 1, 1, 1, 1, 1], 
       [1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
       [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
       [1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
       [1, 1, 1, 0, 0, 0, 1, 0, 0, 1], 
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
       [1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
       [1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

colors = [None, (255, 255, 255), (241, 156, 187)]

pixels_per_radian = screen_width / player_fov
radians_per_rect = player_fov / num_rects

def cache_player_pose():
    global player_prev_x, player_prev_y, player_prev_rot
    player_prev_x = playerx
    player_prev_y = playery
    player_prev_rot = player_rotation
    
def revert_cached_player_pose():
    global playerx, playery, player_rotation
    playerx = player_prev_x
    playery = player_prev_y
    player_rotation = player_prev_rot

def raycast(castangle):
    cx = playerx
    cy = playery
    dx = math.cos(castangle) * 0.1
    dy = -math.sin(castangle) * 0.1
    done = False
    while done == False:
        cx += dx
        cy += dy
        if cy < 0 or cy > len(gmp)-1 or cx < 0 or cx > len(gmp[0])-1:
            done = True
            break
        if gmp[int(cy)][int(cx)] == 1:
            done = True
            break
    return math.hypot(cx - playerx, cy - playery)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            flashlightOn = not flashlightOn
            
    w.fill((0, 0, 0))
    
    dt = c.get_time() / 1000.0

    # teleport player back into room if player leaves bounds of map
    if playery < 0.0 or playery > len(gmp) - 1 or playerx < 0.0 or playerx > len(gmp[0]) - 1:
        playerx = 5.0
        playery = 3.0
    
    cache_player_pose()
    
    d1 = player_rotation - (math.pi / 2)
    d2 = player_rotation + (math.pi / 2)
    d3 = player_rotation + math.pi
    if tsk.get_key_pressed(pygame.K_s):
        playerx += player_move_speed * math.cos(d3) * dt
        playery -= player_move_speed * math.sin(d3) * dt
    if tsk.get_key_pressed(pygame.K_w):
        playerx += player_move_speed * math.cos(player_rotation) * dt
        playery -= player_move_speed * math.sin(player_rotation) * dt
    if tsk.get_key_pressed(pygame.K_a):
        playerx += player_move_speed * math.cos(d1) * dt
        playery -= player_move_speed * math.sin(d1) * dt
    if tsk.get_key_pressed(pygame.K_d):
        playerx += player_move_speed * math.cos(d2) * dt
        playery -= player_move_speed * math.sin(d2) * dt
    if tsk.get_key_pressed(pygame.K_o):
        player_rotation -= player_rot_speed * dt
    if tsk.get_key_pressed(pygame.K_p):
        player_rotation += player_rot_speed * dt
    
    if gmp[int(playery)][int(playerx)] == 1:
        revert_cached_player_pose()
    
    castangle = player_rotation - (player_fov / 2.0)
    while castangle < player_rotation + (player_fov / 2.0):
        r = raycast(castangle)
        rect_height_relative = 1 / r
        rect_height_absolute = rect_height_relative * screen_height
        half_rect_height = rect_height_absolute / 2
        pixels_per_rect = pixels_per_radian * radians_per_rect
        delta = castangle - (player_rotation - (player_fov / 2.0))
        rekt = pygame.Rect(int(delta * pixels_per_radian), int((screen_height / 2) - half_rect_height), int(pixels_per_rect), int(rect_height_absolute))
        brightness = rect_height_relative * 255
        if r <= 1:
            brightness = 255
        if flashlightOn == False:
            brightness /= 4
        brightness = int(brightness)
        pygame.draw.rect(w, (brightness, brightness, brightness), rekt)
        castangle += radians_per_rect

    pygame.display.flip()
    c.tick(60)





# Turn in your Coding Exercise.
