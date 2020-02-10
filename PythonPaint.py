"""
LESSON: TechSmart Studio Project
"""

#### ---- SETUP ---- ####

# --- Libraries --- #

# A1:
import pygame
pygame.init()
import tsk

WIDTH = 600
HEIGHT = 600

PALETTE = [(0,0,0),
           (255,255,255),
           (255,0,0),
           (255,130,0),
           (255,255,0),
           (0,255,0),
           (0,255,255),
           (0,0,255),
           (150,50,255),
           (255,0,255),
           (255,150,200),
           (150,75,0)]
           
paletteDX = WIDTH / len(PALETTE)
paletteDY = 30
brushSize = 10
drawColor = (0, 0, 0)
polygonPoints = []

w = pygame.display.set_mode([WIDTH, HEIGHT])

def drawPal():
    i = 0
    while i < len(PALETTE):
        rekt = pygame.Rect(int(i * paletteDX), 0, int(paletteDX), paletteDY)
        pygame.draw.rect(w, PALETTE[i], rekt)
        i += 1
        
def mouseInPal(my):
    return my >= 0 and my <= paletteDY + brushSize

def clearScreen():
    w.fill((255, 255, 255))

def drawCrossHair(mx, my):
    invR = 0
    invG = 0
    invB = 0
    pygame.draw.line(w, (invR, invG, invB), (mx - 2, my), (mx + 2, my), 1)
    pygame.draw.line(w, (invR, invG, invB), (mx, my - 2), (mx, my + 2), 1)
    pygame.display.flip()
    
running = True
painting = False

prevMx = -1
prevMy = -1
prevPainting = False

drawPal()

while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouseInPal(my):
                palIdx = mx / paletteDX
                drawColor = PALETTE[int(palIdx)]
            else:
                painting = True
        if event.type == pygame.MOUSEBUTTONUP:
            painting = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if brushSize >= 1:
                    brushSize -= 1
            elif event.key == pygame.K_UP:
                if brushSize <= 60:
                    brushSize += 1
            elif event.key == pygame.K_m:
                polygonPoints.append((mx, my))
                drawCrossHair(mx, my)
            elif event.key == pygame.K_p:
                pygame.draw.polygon(w, drawColor, polygonPoints)
                polygonPoints = []
            elif event.key == pygame.K_SPACE:
                clearScreen()
                drawPal()
                    
    
    if painting:
        if mouseInPal(my) == False:
            if prevPainting:
                if mx != prevMx and my != prevMy:
                    pygame.draw.line(w, drawColor, (mx,my), (prevMx,prevMy), int(brushSize * 1.8))
            pygame.draw.circle(w, drawColor, (mx,my), brushSize)
            prevMx = mx
            prevMy = my
            prevPainting = True
    else:
        prevPainting = False
            
    pygame.display.flip()


# Turn in your Coding Project.
