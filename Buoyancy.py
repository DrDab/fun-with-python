"""
LESSON: 5.2 - Spritesheet Animation
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
"""

# Turn in your Coding Exercise.
import pygame
import pygame.freetype
pygame.init()
import math
import tsk

fontDefault = pygame.freetype.SysFont('Arial', 12)
fontDefault.fgcolor = (0, 0, 0)
fontDefault.size = 15

w = pygame.display.set_mode([800, 800])
c = pygame.time.Clock()

# 2D vector class to represent directional quantities.
# all angular measures are in radians.
class Vector2:
    x = 0.0
    y = 0.0
        
    # constructor for vector with arbitrary x and y components
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    @staticmethod
    def CreateNormalized(angle):
        return Vector2(math.cos(angle), math.sin(angle))
      
    def getMagnitude(self):
        return math.hypot(self.x, self.y)
    
    def getNormalized(self):
        magnitude = self.getMagnitude()
        return Vector2(self.x / magnitude, self.y / magnitude)
    
    def getAngle(self):
        return math.atan2(self.y, self.x)        
    
    def scalarMultiply(self, factor):
        return Vector2(self.x * factor, self.y * factor)
    
    def getAdded(self, vector):
        return Vector2(self.x + vector.x, self.y + vector.y)
    
    def getSubtracted(self, vector):
        return Vector2(self.x - vector.x, self.y - vector.y)
        
    def dot(self, vector):
        return (self.x * vector.x) + (self.y * vector.y) 
    
    def add(self, vector):
        self.x += vector.x
        self.y += vector.y
        
    def toTuple(self):
        return (self.x, self.y)
            
    def __str__(self):
        return ("(%.6f, %.6f)" % (self.x, self.y))

class PhysicsVariables:
    g = 10 # m/s^2
    airDensity = 1.20 # kg/m^3

class PhysicsSprite:
    mass = None
    buoyantForce = None
    gravitationalForce = None
    netMomentum = None
    position = None
    volume = None
    sprite = None
    velocity = None
    
    def __init__(self, position, mass, volume):
        self.position = position
        self.mass = mass
        self.volume = volume
        self.velocity = Vector2(0, 0)
        self.gravitationalForce = Vector2(0, mass * PhysicsVariables.g)
        self.buoyantForce = Vector2(0, -PhysicsVariables.airDensity * PhysicsVariables.g * volume)
        self.netMomentum = Vector2(0, 0)
        self.sprite = tsk.Sprite("BalloonRed.png", 0, 0)
        self.sprite.scale = 0.2
        
    def setMass(self, mass):
        self.mass = mass
        self.gravitationalForce = Vector2(0, mass * PhysicsVariables.g)
        
    def setVolume(self, volume):
        self.volume = volume
        self.buoyantForce = Vector2(0, -PhysicsVariables.airDensity * PhysicsVariables.g * volume)
    
    def updateForces(self):
        self.gravitationalForce = Vector2(0, self.mass * PhysicsVariables.g)
        self.buoyantForce = Vector2(0, -PhysicsVariables.airDensity * PhysicsVariables.g * self.volume)
        
    def integrateKinematics(self, dt):
        netForce = self.buoyantForce.getAdded(self.gravitationalForce)
        self.netMomentum.add(netForce.scalarMultiply(dt))
        self.velocity = self.netMomentum.scalarMultiply(1.0 / self.mass)
        self.position.add(self.velocity.scalarMultiply(dt))
        
    def draw(self, debug):
        if debug:
            fontDrawPos = self.position.getAdded(Vector2(25, 25))
            fontDefault.render_to(w, fontDrawPos.toTuple(), "m=%.3fkg" % self.mass)
            fontDefault.render_to(w, fontDrawPos.getAdded(Vector2(0, 15)).toTuple(), "V=%.3fm^3" % self.volume)
            fontDefault.render_to(w, fontDrawPos.getAdded(Vector2(0, 30)).toTuple(), "Force(N):Grav=%s, Buoy=%s" % (self.gravitationalForce, self.buoyantForce))
            fontDefault.render_to(w, fontDrawPos.getAdded(Vector2(0, 45)).toTuple(), "Velocity=%s m/s" % (self.velocity))
        self.sprite.center = self.position.toTuple()
        self.sprite.draw()

          
explosionSheet = tsk.ImageSheet("ExplosionSheet.png", 4, 6)
balloons = []

def clear():
        w.fill((255, 255, 255))

debug = False
animating = True
running = True
while running:
    clear()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            balloons.append(PhysicsSprite(Vector2(mx, my), 0.002, 0.008))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and PhysicsVariables.airDensity > 0.00:
                PhysicsVariables.airDensity -= 0.05
            if event.key == pygame.K_UP:
                PhysicsVariables.airDensity += 0.05
            if event.key == pygame.K_LEFT:
                PhysicsVariables.g -= 0.1
            if event.key == pygame.K_RIGHT:
                PhysicsVariables.g += 0.1
            if event.key == pygame.K_SPACE:
                debug = not debug
            if event.key == pygame.K_p:
                animating = not animating
    
    dt = c.get_time() / 1000.0
    
    for balloon in balloons:
        if balloon.position.y <= 50 + (0.1 * balloon.netMomentum.scalarMultiply(1.0 / balloon.mass).getMagnitude()):
            if (balloon.sprite.image == explosionSheet) == False:
                balloon.sprite.image = explosionSheet
                balloon.sprite.image_animation_rate = 35
                balloon.sprite.scale = 0.2
            balloon.sprite.update(c.get_time())
        if balloon.position.y < 0:
            balloons.remove(balloon)
            continue
        balloon.updateForces()
        if animating:
            balloon.integrateKinematics(dt)
        balloon.draw(debug)
        
    fontDefault.render_to(w, (0, 0), "Air density=%.3f kg/m^3" % PhysicsVariables.airDensity)
    fontDefault.render_to(w, (0, 15), "g=%.2f m/s^2" % PhysicsVariables.g)
    
    pygame.display.flip()
    c.tick(30)
                            
            
    
