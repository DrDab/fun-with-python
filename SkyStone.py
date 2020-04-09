"""
LESSON: 6.1 - Functions
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
"""

import pygame
import pygame.freetype
import tsk
import math

# screen constants.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# game constants.
FEET_PER_PIXEL = 12.0 / SCREEN_WIDTH
PLAYER_DIAGONAL_SIZE = math.sqrt(2*(1.5*1.5)) # ft
MAX_Y_SPEED = 3.0 # ft/s
MAX_X_SPEED = 1.5 # ft/s
MAX_ANGULAR_SPEED = math.pi # rad/s

def scale_to_pixels(feet):
    return feet / FEET_PER_PIXEL

# player pose variables.
playerx = scale_to_pixels(9.0 / 12.0)
playery = scale_to_pixels(6.0)
playerrot = math.pi * 1.75

# skystone pose variables.
# blue foundation
blue_foundation_x = scale_to_pixels(4.6875)
blue_foundation_y = scale_to_pixels(1.78645833)
blue_foundation_rot = math.pi * 1.75
# red foundation
red_foundation_x = scale_to_pixels(12.0 - 4.6875)
red_foundation_y = scale_to_pixels(1.78645833)
red_foundation_rot = math.pi * 1.75

# other gameplay variables.
fps = 60.0 # measured framerate

def get_player_points():
    p1 = (playerx + (half_player_diagonal * math.cos(playerrot)), playery + (half_player_diagonal * math.sin(playerrot)))
    p2 = (playerx + (half_player_diagonal * math.sin(playerrot)), playery - (half_player_diagonal * math.cos(playerrot)))
    p3 = (playerx - (half_player_diagonal * math.cos(playerrot)), playery - (half_player_diagonal * math.sin(playerrot)))
    p4 = (playerx - (half_player_diagonal * math.sin(playerrot)), playery + (half_player_diagonal * math.cos(playerrot)))
    return [p1, p2, p3, p4]

def get_red_foundation_points():
    return 

prev_player_pose_x = 0.0
prev_player_pose_y = 0.0
prev_player_pose_rot = 0.0
def cache_player_pose():
    global prev_player_pose_x, prev_player_pose_y, prev_player_pose_rot
    prev_player_pose_x = playerx
    prev_player_pose_y = playery
    prev_player_pose_rot = playerrot

def revert_cached_player_pose():
    global playerx, playery, playerrot
    playerx = prev_player_pose_x
    playery = prev_player_pose_y
    playerrot = prev_player_pose_rot

def draw_player(points):
    pygame.draw.polygon(w, (95, 102, 102), points)
    pygame.draw.circle(w, (0, 0, 0), (int(playerx + ((PLAYER_DIAGONAL_SIZE * math.cos(playerrot - (math.pi / 4)) / (2 * FEET_PER_PIXEL)))), int(playery + ((PLAYER_DIAGONAL_SIZE * math.sin(playerrot - (math.pi / 4)) / (2 * FEET_PER_PIXEL))))), 2)

# skystone field points.
blue_building_corner_p1 = (scale_to_pixels(22.75 / 12.0), 0)
blue_building_corner_p2 = (0, scale_to_pixels(22.75 / 12.0))
red_building_corner_p1 = (scale_to_pixels(12.0 - (22.75 / 12.0)), 0)
red_building_corner_p2 = (scale_to_pixels(12), scale_to_pixels(22.75 / 12.0))
blue_loading_corner_p1 = (0, scale_to_pixels(12.0 - (22.75 / 12.0)))
blue_loading_corner_p2 = (scale_to_pixels(22.75 / 12.0), scale_to_pixels(12.0 - (22.75 / 12.0)))
blue_loading_corner_p3 = (scale_to_pixels(22.75 / 12.0), scale_to_pixels(12.0))
red_loading_corner_p1 = (scale_to_pixels(12), scale_to_pixels(12.0 - (22.75 / 12.0)))
red_loading_corner_p2 = (scale_to_pixels(12.0 - (22.75 / 12.0)), scale_to_pixels(12.0 - (22.75 / 12.0)))
red_loading_corner_p3 = (scale_to_pixels(12.0 - (22.75 / 12.0)), scale_to_pixels(12))
skybridgeNeutralRect = pygame.Rect(int(scale_to_pixels(4 - (2.0 / 12.0))), int(scale_to_pixels(5.25)), int(scale_to_pixels(4 + (4.0 / 12.0))), int(scale_to_pixels(1.5)))
blue_midline_p1 = (0, scale_to_pixels(6))
blue_midline_p2 = (scale_to_pixels(46.0 / 12.0), scale_to_pixels(6))
red_midline_p1 = (scale_to_pixels(12), scale_to_pixels(6))
red_midline_p2 = (scale_to_pixels(12.0 - (46.0 / 12.0)), scale_to_pixels(6))
yellow_midline_p1_upper = (scale_to_pixels(46.0 / 12.0), scale_to_pixels(6 - 0.1875))
yellow_midline_p2_upper = (scale_to_pixels(12.0 - (46.0 / 12.0)), scale_to_pixels(6 - 0.1875))
yellow_midline_p1_lower = (scale_to_pixels(46.0 / 12.0), scale_to_pixels(6 + 0.1875))
yellow_midline_p2_lower = (scale_to_pixels(12.0 - (46.0 / 12.0)), scale_to_pixels(6 + 0.1875))

def draw_skystone_field():
    pygame.draw.line(w, (0, 0, 255), blue_building_corner_p1, blue_building_corner_p2, int(scale_to_pixels(2.0 / 12.0)))
    pygame.draw.line(w, (255, 0, 0), red_building_corner_p1, red_building_corner_p2, int(scale_to_pixels(2.0 / 12.0)))
    pygame.draw.line(w, (255, 0, 0), blue_loading_corner_p1, blue_loading_corner_p2, int(scale_to_pixels(2.0 / 12.0)))
    pygame.draw.line(w, (255, 0, 0), blue_loading_corner_p2, blue_loading_corner_p3, int(scale_to_pixels(2.0 / 12.0)))
    pygame.draw.line(w, (0, 0, 255), red_loading_corner_p1, red_loading_corner_p2, int(scale_to_pixels(2.0 / 12.0)))
    pygame.draw.line(w, (0, 0, 255), red_loading_corner_p2, red_loading_corner_p3, int(scale_to_pixels(2.0 / 12.0)))
    pygame.draw.rect(w, (47, 79, 79), skybridgeNeutralRect)
    pygame.draw.line(w, (0, 0, 255), blue_midline_p1, blue_midline_p2, int(scale_to_pixels(1.0 / 12.0)))
    pygame.draw.line(w, (255, 0, 0), red_midline_p1, red_midline_p2, int(scale_to_pixels(1.0 / 12.0)))
    pygame.draw.line(w, (255, 255, 0), yellow_midline_p1_upper, yellow_midline_p2_upper, int(scale_to_pixels(1.0 / 12.0)))
    pygame.draw.line(w, (255, 255, 0), yellow_midline_p1_lower, yellow_midline_p2_lower, int(scale_to_pixels(1.0 / 12.0)))

#def draw_dynamic_game_pieces():
#

def check_collision(points):
    for point in points:
        if point[0] < 0 or point[0] > SCREEN_WIDTH:
            return True
        if point[1] < 0 or point[1] > SCREEN_HEIGHT:
            return True
        if point[0] > skybridgeNeutralRect.x and point[0] < skybridgeNeutralRect.x + skybridgeNeutralRect.width and point[1] > skybridgeNeutralRect.y and point[1] < skybridgeNeutralRect.y + skybridgeNeutralRect.height:
            return True
    return False

pygame.init()
w = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
c = pygame.time.Clock()

font = pygame.freetype.SysFont('Arial', 12)
font.size = 20

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    w.fill((223, 223, 223))

    # check for player movement commands.
    # recalculate robot pose based on commands.
    # if there is a collision with a wall (check each point), then undo the movement with the previous pose.
    cache_player_pose()
    robot_y_angle = playerrot - (math.pi / 4)
    robot_x_angle = playerrot + (math.pi / 4)
    half_player_diagonal = PLAYER_DIAGONAL_SIZE / (2.0 * FEET_PER_PIXEL)
    if tsk.get_key_pressed(pygame.K_o):
        playerrot -= MAX_ANGULAR_SPEED / fps
    if tsk.get_key_pressed(pygame.K_p):
        playerrot += MAX_ANGULAR_SPEED / fps
    if tsk.get_key_pressed(pygame.K_w):
        playerx += (MAX_Y_SPEED / (FEET_PER_PIXEL * fps)) * math.cos(robot_y_angle)
        playery += (MAX_Y_SPEED / (FEET_PER_PIXEL * fps)) * math.sin(robot_y_angle)
    elif tsk.get_key_pressed(pygame.K_s):
        playerx += (MAX_Y_SPEED / (FEET_PER_PIXEL * fps)) * math.cos(robot_y_angle - math.pi)
        playery += (MAX_Y_SPEED / (FEET_PER_PIXEL * fps)) * math.sin(robot_y_angle - math.pi)
    elif tsk.get_key_pressed(pygame.K_a):
        playerx += (MAX_X_SPEED / (FEET_PER_PIXEL * fps)) * math.cos(robot_x_angle - math.pi)
        playery += (MAX_X_SPEED / (FEET_PER_PIXEL * fps)) * math.sin(robot_x_angle - math.pi)
    elif tsk.get_key_pressed(pygame.K_d):
        playerx += (MAX_X_SPEED / (FEET_PER_PIXEL * fps)) * math.cos(robot_x_angle)
        playery += (MAX_X_SPEED / (FEET_PER_PIXEL * fps)) * math.sin(robot_x_angle)

    player_points = get_player_points()
    if check_collision(player_points):
        revert_cached_player_pose()

    # draw player robot.
    draw_skystone_field()
    draw_player(player_points)
    font.render_to(w, (0, 0), "FTC Mechanum Bot Simulator 2020")
    font.render_to(w, (0, 20), "Use [W][A][S][D] keys to move and [O] and [P] to rotate robot")
    pygame.display.flip()
    c.tick(60)
    fps = 1000 / c.get_time()
# Turn in your Coding Exercise.
