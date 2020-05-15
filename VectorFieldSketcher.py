"""
LESSON: 6.2 - Return Values
EXERCISE: Code Your Own

TITLE: Vector Field Drawer
DESCRIPTION: [Your Description Here]
"""
import pygame
pygame.init()
import tsk
import math

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 600
VECTOR_GAP = 50
STOP_DISTANCE = math.sqrt(2*VECTOR_GAP*VECTOR_GAP)

num_rows = int(SCREEN_HEIGHT / VECTOR_GAP)
num_cols = int(SCREEN_WIDTH / VECTOR_GAP)
screen_diagonal_dist = math.hypot(SCREEN_HEIGHT, SCREEN_WIDTH)

# returns a list containing the two X and Y points of the vector to draw a line with.
def getVectorPose(row, col, mouseX, mouseY):
    vectorPX = row * VECTOR_GAP
    vectorPY = col * VECTOR_GAP
    dy = vectorPY - mouseY
    dx = vectorPX - mouseX
    dist = math.hypot(dy, dx)
    if dist <= STOP_DISTANCE:
        return [vectorPX, vectorPY, vectorPX, vectorPY]
    unitDy = dy / dist
    unitDx = dx / dist
    relDist = dist / screen_diagonal_dist
    vectorPoseMagnitude = relDist ** -2
    half_vectorPoseMagnitude = vectorPoseMagnitude / 2
    halfVectorDx = unitDx * half_vectorPoseMagnitude
    halfVectorDy = unitDy * half_vectorPoseMagnitude
    p1X = vectorPX + halfVectorDx
    p1Y = vectorPY + halfVectorDy
    p2X = vectorPX - halfVectorDx
    p2Y = vectorPY - halfVectorDy
    return [p1X, p1Y, p2X, p2Y]

def drawAllVectors(mouseX, mouseY, window):
    for i in range(0, num_rows):
        for j in range(0, num_cols):
            pose = getVectorPose(i, j, mouseX, mouseY)
            pygame.draw.line(window, (0, 0, 0), (pose[0],pose[1]), (pose[2], pose[3]), 2)
    pygame.display.flip()
    
w = pygame.display.set_mode([SCREEN_HEIGHT, SCREEN_WIDTH])
c = pygame.time.Clock()
running = True
while running:
    w.fill([255, 255, 255])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
            
    mx, my = pygame.mouse.get_pos()
    drawAllVectors(mx, my, w)
    c.tick(60)
    

# Turn in your Coding Exercise.
