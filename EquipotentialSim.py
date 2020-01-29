"""
LESSON: 3.1 - Lines
EXERCISE: Code Your Own

TITLE: Equipotential Line Grapher
DESCRIPTION: [Your Description Here]
"""

import pygame
import math
pygame.init()

K = 9.0 * (10 ** 9) # N * m^2 * c^-2

# particle colors.
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 10-cm tick mark colors.
AMARANTH_PINK = (247, 168, 184)

charges = [] # 2d array, each row has 3 cols, rep. x y c

def calcVoltage(charge, distance):
    if distance == 0.0:
        return 234323343445353454532185.0
    return (K * charge * (10 ** -9)) / (distance / 100.0)

def ib(test, tgt, p):
    return abs(test - tgt) <= p

def dist(dx, dy):
    return math.sqrt((dx * dx) + (dy * dy))

def voltagesum(x, y):
    vsum = 0.0
    for charge in charges:
        cdist = dist(charge[0] - x, charge[1] - y)
        voltage = calcVoltage(charge[2], cdist)
        vsum += voltage
        #print(vsum)
    return vsum

def dohelp():
    print("COMMANDS")
    print("p <x> <y> <c> - adds a positive charge at coordinates x,y, with charge magnitude c.")
    print("n <x> <y> <c> - adds a negative charge at coordinates x,y, with charge magnitude c.")
    print("v <x> <y> - prints the total voltage at a given point w/ coordinates x, y.")
    print("g <v> [p] - redraws the equipotential graph for a given voltage, within voltage tolerance p. If p omitted, tolerance default = 0.5V")
    print("d <i> - deletes a charge at index i. (zero-based)")
    print("\"dall\" - deletes all charges.")
    print("l - lists all charges")
    print("c - clears console")
    print("e - erase results")
    print("\"quit\" - quit program")
    print("Position units are in centimeters. Charge units are in nanocoulombs.")
    print("8 pixels maps to a centimeter.")


def drawcharges():
    for charge in charges:
        cx = charge[0]
        cy = charge[1]
        cc = charge[2]
        cx_s = cx * 8.0
        cy_s = cy * 8.0
        color = None
        if cc > 0:
            color = RED
        else:
            color = BLUE
        pygame.draw.circle(w, color, (cx_s, cy_s), 10)      
    pygame.display.flip()

# draw 10-centimeter tickmarks.
def drawticks():
    furry = 0
    while furry < 800:
        if furry % 80 == 0:
            pygame.draw.circle(w, AMARANTH_PINK, (0, furry), 2)
            pygame.draw.circle(w, AMARANTH_PINK, (1, furry), 2)
            pygame.draw.circle(w, AMARANTH_PINK, (furry, 0), 2)
            pygame.draw.circle(w, AMARANTH_PINK, (furry, 1), 2)
        furry += 1
    pygame.display.flip()

def clearscreen():
    w.fill([0, 0, 0])
    drawticks()
    pygame.display.flip()
        
w = pygame.display.set_mode([800, 800])
clearscreen()

print("Doki's Equipotential Line Grapher, Mk. I")
print("Copyright (C) Doki Husky 2019")
print("Type \"help\" for help.")
print()
dohelp()

while True:
    try:
        choice = input().strip().lower()
        params = choice.split()
        if choice == "quit":
            print("Goodbye")
            raise SystemExit
        elif choice == "help":
            dohelp()
        elif choice == "c":
            furry = 0
            while furry < 200:
                print()
                furry += 1
        elif params[0] == "p":
            x = float(params[1])
            y = float(params[2])
            c = abs(float(params[3]))
            charges.append([x, y, c])
            print("Added positive charge (%.2f, %.2f) cm, %.2f nC" % (x, y, c))
        elif params[0] == "n":
            x = float(params[1])
            y = float(params[2])
            c = abs(float(params[3]))
            charges.append([x, y, -c])
            print("Added negative charge (%.2f, %.2f) cm, %.2f nC" % (x, y, c))
        elif params[0] == "g":
            print("Please wait 10 seconds.")
            v = float(params[1])
            p = 0.5
            if len(params) == 3:
                p = float(params[2])
            xpx = 0
            ypx = 0
            while xpx < 800:
                ypx = 0
                while ypx < 800:
                    cx = xpx / 8.0
                    cy = ypx / 8.0
                    vp = voltagesum(cx, cy)
                    if ib(vp, v, p):
                        pygame.draw.circle(w, (255, 255, 255), (xpx, ypx), 2)
                    ypx += 4
                xpx += 4            
            pygame.display.flip()
            print("Regraphed equipotential lines with voltage %.2f" % (v))
        elif params[0] == "v":
            x = float(params[1])
            y = float(params[2])
            voltage = voltagesum(x, y)
            print("Voltage at (%.2f, %.2f) cm: %.2f" % (x, y, voltage))
        elif params[0] == "l":
            print(charges)
        elif params[0] == "d":
            i = int(params[1])
            charges.pop(i)
            clearscreen()
            print("Removed item %d" % i)
        elif params[0] == "dall":
            charges = []
            print("Removed all items.")
            clearscreen()
        elif params[0] == "e":
            clearscreen()
            print("Results cleared.")
        
        # draw all the charges.
        # positive charges are red, negative charges blue
        drawcharges()
        
    except Exception as e:
        print("Error: " + str(e))








# Turn in your Coding Exercise.
