"""
LESSON: 4.3 - For Range
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
"""
import pygame
import pygame.freetype

class RobotState:
    x = None
    y = None
    delay = None
    def __init__(self, x, y, delay):
        self.x = x
        self.y = y
        self.delay = delay

poses = []

width = 800
height = 800
pygame.init()
w = pygame.display.set_mode([width, height])

font = pygame.freetype.SysFont('Arial', 12)
font.size = 10
font.render_to(w, (0,0), "Press [SPACE] to draw the pattern.")
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = False
                break
        if event.type == pygame.MOUSEBUTTONDOWN:
            w.fill((255, 255, 255))
            x,y = pygame.mouse.get_pos()
            poses.append(RobotState(x,y,200))
            i = 0
            while i < len(poses):
                pose = poses[i]
                pygame.draw.circle(w, (0, 0, 0), (pose.x,pose.y), 5)
                font.render_to(w, (pose.x+10,pose.y+10), "%d"%(i+1))
                i += 1
            pygame.display.flip()
            

isDraw = True
while True:
    if isDraw:
        for i in range(len(poses)):
            w.fill((255, 255, 255))
            pose = poses[i]
            if i > 0:
                j = i
                while j > 0:
                    pygame.draw.line(w, (0, 0, 0), (poses[j].x,poses[j].y), (poses[j-1].x, poses[j-1].y), 2)
                    j -= 1
            pygame.draw.circle(w, (0, 0, 0), (pose.x, pose.y), 20)
            pygame.display.flip()
            pygame.time.wait(pose.delay)
    print("Type \"repeat\" to watch it again")
    print("Type \"polygon\" to make a wacky polygon")
    print("Type \"quit\" to quit")
    s = input()
    if s == "quit":
        break
    if s == "polygon":
        isDraw = False
        points = []
        for pose in poses:
            points.append((pose.x,pose.y))
        pygame.draw.polygon(w, (0, 0, 0), points)
        pygame.display.flip()
    if s == "repeat":
        isDraw = True







# Turn in your Coding Exercise.
