"""
BallisticsSimV2

Description:
"""

import math
import pygame

# CONSTANTS, USER-EDITABLE
G = 6.67 * (10 ** -11) # universal gravitational constant, m^3 * kg^-1 * s^-2 
EARTH_RADIUS = 6.3781 * (10 ** 6) # radius of earth, meters
EARTH_MASS = 6.3781 * (10 ** 24) # mass of planet earth, kg
AIR_DENSITY = 1.204 # kg * m^-3
DT = 0.001 # time step for Riemann integration of velocity/position, seconds
standard_g = 9.8 # standard gravitational acceleration if g is to be assumed as constant, m * s^-2
CONSTANT_GRAVITY = False
DEBUG = False
DRAW_TRAJECTORY = True
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# END CONSTANTS

# method to take numerical input and validate it.
def getf():
    while True:
        try:
            return float(input())
        except Exception as e:
            print("Please enter a valid floating-point value.")
            
def geti():
    while True:
        try:
            return int(input())
        except Exception as e:
            print("Please enter a valid integer value.")

# auxiliary methods to compute and convert information
def compute_air_drag(drag_coefficient, csec_area, velocity_magnitude):
    return 0.5 * drag_coefficient * AIR_DENSITY * csec_area * (velocity_magnitude ** 2)

def compute_gravitational_force(projectile_mass, radius):
    if CONSTANT_GRAVITY:
        return standard_g * projectile_mass
    return (G * EARTH_MASS * projectile_mass) / (radius * radius)

def magnitude(input_vector):
    return math.sqrt((input_vector[0] * input_vector[0]) + (input_vector[1] * input_vector[1]))

def unit_vector(input_vector):
    mag = magnitude(input_vector)
    return [input_vector[0] / mag, input_vector[1] / mag]

def negate_vector(input_vector):
    return [-input_vector[0], -input_vector[1]]

def degrees_to_radians(degrees):
    return (degrees * 3.1415926) / 180.0

position_vector = [0.0, 0.0] # position vector of projectile, meters
momentum_vector = [0.0, 0.0] # momentum vector of projectile, kg^1 * m^-1 ^ s^-1
force_vector = [0.0, 0.0] # net force on each axis of projectilke, kg * m * s^-2
air_drag = False # consider air drag?
drag_coefficient = 0.0 # drag coefficient of projectile
csec_area = 0.0 # cross sectional area of projecitle, m^2

print("Welcome to the Furry Defense Force Ballistics Simulation System, Mk.III")
print("Copyright (C) Doki Husky 2019")
print()
print()
print("Enable support for aerodynamic drag integration? (Y/N)")
air_drag = input().lower().strip()[0] == "y"

if air_drag:
    print("What is the drag coefficient of the projectile?")
    drag_coefficient = getf()
    print("What is the cross-sectional area of the projectile? (m^2)")
    csec_area = getf()

print("What is the mass of the projectile? (kg)")
object_mass = getf()

print("What is the launch angle of the projectile? (degrees)")
launch_angle = degrees_to_radians(getf())

print("What is the launch velocity of the projectile? (m/s)")
launch_velocity = getf()

print("What is the time to compute the trajectory to? (s)")
max_time = getf()

print("Make data desmos-graphable? (Y/N)")
desmos = input().lower().strip()[0] == "y"

print("Integrator step delta for each point? (ms)")
stepdelta = geti()

momentum_init_magnitude = object_mass * launch_velocity
momentum_vector[0] = momentum_init_magnitude * math.cos(launch_angle)
momentum_vector[1] = momentum_init_magnitude * math.sin(launch_angle)

w = None
screen_mid = SCREEN_HEIGHT / 2

if DRAW_TRAJECTORY:
    pygame.init()
    w = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    w.fill([0, 0, 0])
    # draw 100-meter tickmarks on X and Y axis.
    tm = 0
    while tm < SCREEN_WIDTH:
        if tm % 100 == 0:
            pygame.draw.circle(w, (255, 180, 105), (tm, screen_mid - 1), 2)
            pygame.draw.circle(w, (255, 180, 105), (tm, screen_mid), 2)
            pygame.draw.circle(w, (255, 180, 105), (tm, screen_mid + 1), 2)
        tm += 1
    tm = 0
    while tm < screen_mid:
        if tm % 100 == 0:
            pygame.draw.circle(w, (255, 180, 105), (0, screen_mid + tm), 2)
            pygame.draw.circle(w, (255, 180, 105), (1, screen_mid + tm), 2)
            pygame.draw.circle(w, (255, 180, 105), (0, screen_mid - tm), 2)
            pygame.draw.circle(w, (255, 180, 105), (1, screen_mid - tm), 2)
        tm += 1
    pygame.display.flip()

print()
print()
print("----- BEGIN PROJECTILE DROP TABLE -----")
if desmos:
    print("x (m), y (m)")
else:
    print("time(s), x (m), y (m)")

steps = 0
cur_time = 0.0
while cur_time <= max_time:
    # print the current time, and position x and y.
    if steps % stepdelta == 0:
        if desmos:
            print("%.2f, %.2f" % (position_vector[0], position_vector[1]))
        else:
            print("%.2f, %.2f, %.2f" % (cur_time, position_vector[0], position_vector[1]))
            
        if DRAW_TRAJECTORY:
            scaledx = position_vector[0]
            scaledy = screen_mid - position_vector[1]
            pygame.draw.circle(w, (255, 255, 255), (scaledx, scaledy), 2)
            pygame.display.flip()
    
    # compute the net force on each axis.
    
    # calculate gravitational force
    force_vector = [0.0, 0.0]
    gravity_force = -compute_gravitational_force(object_mass, EARTH_RADIUS + position_vector[1])
    force_vector[1] += gravity_force
    if DEBUG:
        print("GravForce=[%.2f, %.2f], " % (0.0, gravity_force), end = '')
    
    # calculate aerodynamic drag force
    if air_drag:
        vel_vector = [momentum_vector[0] / object_mass, momentum_vector[1] / object_mass]
        vel_unit_vector_negated = negate_vector(unit_vector(vel_vector))
        velocity_magnitude = magnitude(vel_vector)
        drag_force_magnitude = compute_air_drag(drag_coefficient, csec_area, velocity_magnitude)
        drag_x = drag_force_magnitude * vel_unit_vector_negated[0]
        drag_y = drag_force_magnitude * vel_unit_vector_negated[1]
        force_vector[0] += drag_x
        force_vector[1] += drag_y
        if DEBUG:
            print("DragForce=[%.2f, %.2f]" % (drag_x, drag_y), end='')
    
    if DEBUG:
        print("\nNetForce=[%.2f, %.2f], NetMomentum=[%.2f, %.2f]" % (force_vector[0], force_vector[1], momentum_vector[0], momentum_vector[1]))
    
    
    # update the momentum on each axis.
    momentum_vector[0] += force_vector[0] * DT
    momentum_vector[1] += force_vector[1] * DT
    
    # finally, update position
    vel_x = momentum_vector[0] / object_mass
    vel_y = momentum_vector[1] / object_mass

    position_vector[0] += vel_x * DT
    position_vector[1] += vel_y * DT

    cur_time += DT
    steps += 1
print("[Enter] to quit.")
input()
# Turn in your Coding Exercise.
