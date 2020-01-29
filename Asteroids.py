"""
LESSON: 4.2 - For Each
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
"""

import pygame
import pygame.freetype
pygame.init()
import random
import math
import time
    
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

# physics and game constants to run with.
class Constants:
    g = -10 # gravitational acceleration, ms^-2
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 800
    # m/pixel = 2.5
    # actual = m/px * px
    # actual dimensions: 2500m x 2000m
    METERS_PER_PIXEL = 2000 / SCREEN_HEIGHT
    BOTTOM_CENTER_POSITION = Vector2(1250, 0)
    SCREEN_MIDDLE_POSITION = Vector2(500, 400)
    LEFT_BOTTOM_POSITION = Vector2(0, 0)
    RIGHT_TOP_POSITION = Vector2(2500, 2000)
    PLAYER_MUZZLE_SPEED = 1200 # player cannon muzzle velocity, ms^-1

# class describing a projectile in terms of kinematics data, and rod length/width, in in-game arbitrary units.
class Projectile:
    position = None
    velocity = None
    acceleration = None
    rod_length = None
    rod_width = None
    
    def __init__(self, pos_x, pos_y, exit_velocity, launch_angle, rod_length, rod_width):
        self.position = Vector2(pos_x, pos_y)
        self.velocity = Vector2.CreateNormalized(launch_angle).scalarMultiply(exit_velocity)
        self.acceleration = Vector2(0, Constants.g)
        self.rod_length = rod_length
        self.rod_width = rod_width
        
    def updatePosition(self, dt):
        self.velocity.add(self.acceleration.scalarMultiply(dt))
        self.position.add(self.velocity.scalarMultiply(dt))
    
    def isColliding(self, enemies, dt):
        for enemy in enemies:
            # TSK server-client lag compensation, calculated projected enemy position and check for collision with projected position.
            enemyProjectedPosition = enemy.position.getAdded(enemy.velocity.scalarMultiply(dt))
            projectile_draw_vector = projectile.velocity.getNormalized().scalarMultiply(projectile.rod_length)
            projectile_head_pos = projectile.position
            projectile_tail_pos = projectile_head_pos.getSubtracted(projectile_draw_vector)
            d1 = math.hypot(enemyProjectedPosition.x - projectile_head_pos.x, enemyProjectedPosition.y - projectile_head_pos.y)
            d2 = math.hypot(enemyProjectedPosition.x - projectile_tail_pos.x, enemyProjectedPosition.y - projectile_tail_pos.y)
            avg = (d1 + d2) / 2
            if avg <= enemy.radius + 40:
                return enemy
        return None
    
    def isOutsideBounds(self, lowerLeft, upperRight):
        if self.position.x < lowerLeft.x:
            return True
        if self.position.y < lowerLeft.y:
            return True
        if self.position.x > upperRight.x:
            return True
        if self.position.y > upperRight.y:
            return True
        
    def __str__(self):
        return ("Pos=%s Vel=%s" % (self.position, self.velocity))

# class to keep track of player health, ammo and gun temperature.
class PlayerStats:
    hp = None
    ammo = None
    temperature = None
    
    def __init__(self, hp, ammo, temperature):
        self.hp = hp
        self.ammo = ammo
        self.temperature = temperature

# drawing utility to draw shapes with locations defined by in-game scaled coordinates instead of pixel coordinates. 
# in the game coordinate system, the origin (0, 0) is located at the bottom-left corner of the screen.
# the +x-direction is right from the origin, and the +y-direction is up from the origin.
# all in-game distances are in meters.
class ScreenUtil:
    width = None
    height = None
    pixels_per_distance = None
    distance_per_pixel = None
    
    def __init__(self, width, height, distance_per_pixel):
        self.width = width
        self.height = height
        self.distance_per_pixel = distance_per_pixel
        self.pixels_per_distance =  1 / distance_per_pixel
        
    def circle(self, w, color, arbitraryPos, arbitraryRadius):
        rightCoords = (self.pixels_per_distance * arbitraryPos[0])
        upCoords = self.height - (self.pixels_per_distance * arbitraryPos[1])
        pygame.draw.circle(w, color, (int(rightCoords), int(upCoords)), int(self.pixels_per_distance * arbitraryRadius))
        
    def alt_circle(self, w, color, arbitraryPos, radius, fill):
        rightCoords = (self.pixels_per_distance * arbitraryPos[0])
        upCoords = self.height - (self.pixels_per_distance * arbitraryPos[1])
        pygame.draw.circle(w, color, (int(rightCoords), int(upCoords)), radius, fill)
        
    def line(self, w, color, arbitraryPos1, arbitraryPos2, width):
        p1 = (self.pixels_per_distance * arbitraryPos1[0], self.height - (self.pixels_per_distance * arbitraryPos1[1]))
        p2 = (self.pixels_per_distance * arbitraryPos2[0], self.height - (self.pixels_per_distance * arbitraryPos2[1]))
        widthScaled = self.pixels_per_distance * width
        pygame.draw.line(w, color, p1, p2, int(widthScaled))
        
    def alt_line(self, w, color, arbitraryPos1, arbitraryPos2, width):
        p1 = (self.pixels_per_distance * arbitraryPos1[0], self.height - (self.pixels_per_distance * arbitraryPos1[1]))
        p2 = (self.pixels_per_distance * arbitraryPos2[0], self.height - (self.pixels_per_distance * arbitraryPos2[1]))
        pygame.draw.line(w, color, p1, p2, int(width))
    
    def rect(self, w, color, bottomLeft, topRight):
        blConverted = bottomLeft.scalarMultiply(self.pixels_per_distance)
        trConverted = topRight.scalarMultiply(self.pixels_per_distance)
        convertedRekt = pygame.Rect(int(blConverted.x), int(self.height - trConverted.y), int(abs(blConverted.x - trConverted.x)), int(abs(blConverted.y - trConverted.y)))
        pygame.draw.rect(w, color, convertedRekt)
    
    def draw_projectile(self, w, projectile):
        projectile_draw_vector = projectile.velocity.getNormalized().scalarMultiply(projectile.rod_length)
        projectile_head_pos = projectile.position
        projectile_tail_pos = projectile_head_pos.getSubtracted(projectile_draw_vector)
        self.line(w, (255, 255, 255), projectile_tail_pos.toTuple(), projectile_head_pos.toTuple(), projectile.rod_width)
    
    def draw_enemy(self, w, enemy):
        self.circle(w, (150, 75, 0), enemy.position.toTuple(), enemy.radius)
    
    def to_game_coords(self, pixelcoords):
        return Vector2(pixelcoords.x, self.height - pixelcoords.y).scalarMultiply(self.distance_per_pixel)
    
    def to_pixel_coords(self, gamecoords):
        return Vector2(gamecoords.x * self.pixels_per_distance, self.height - (gamecoords.y * self.pixels_per_distance))
    
    def clear(self, w):
        w.fill((48, 63, 102))
    
    def flip(self):
        pygame.display.flip()

class GameHUD:
    util = None
    fontDefault = None
    fontLocked = None
    fontBanner = None
    banner = None
    DEFAULT_COLOR = (192, 255, 0)
    LOCKED_COLOR = (255, 0, 0)
    
    def __init__(self, util):
        self.util = util
        self.fontDefault = pygame.freetype.SysFont('Arial', 12)
        self.fontDefault.fgcolor = self.DEFAULT_COLOR
        self.fontDefault.size = 10
        self.fontLocked = pygame.freetype.SysFont('Arial', 12)
        self.fontLocked.fgcolor = self.LOCKED_COLOR
        self.fontLocked.size = 10
        self.fontBanner = pygame.freetype.SysFont('Arial', 12)
        self.fontBanner.fgcolor = self.DEFAULT_COLOR
        self.fontBanner.size = 20
        
    def check_draw_banner(self, w):
        if self.banner != None:
            if time.time() >= self.banner[1]:
                self.banner = None
            else:
                self.fontBanner.render_to(w, Constants.SCREEN_MIDDLE_POSITION.getSubtracted(Vector2(100, 300)).toTuple(), self.banner[0])
    
    
    def draw_enemy_hud_info(self, w, enemy, player_muzzle_velocity, player_angle):
        self.check_draw_banner(w)
        bl = enemy.position.getAdded(Vector2.CreateNormalized(5 * math.pi / 4).scalarMultiply(enemy.radius * 2))
        tr = enemy.position.getAdded(Vector2.CreateNormalized(math.pi / 4).scalarMultiply(enemy.radius * 2))
        tl = bl.getAdded(Vector2(0, tr.y - bl.y))
        br = tr.getAdded(Vector2(0, bl.y - tr.y))
        rectColor = self.DEFAULT_COLOR
        font = self.fontDefault
        if enemy.lockedOn:
            rectColor = self.LOCKED_COLOR
            font = self.fontLocked
        util.alt_line(w, rectColor, bl.toTuple(), tl.toTuple(), 1)
        util.alt_line(w, rectColor, tl.toTuple(), tr.toTuple(), 1)
        util.alt_line(w, rectColor, tr.toTuple(), br.toTuple(), 1)
        util.alt_line(w, rectColor, bl.toTuple(), br.toTuple(), 1)
        font_line_1_location = util.to_pixel_coords(Vector2(br.x, tl.y))
        font_line_2_location = font_line_1_location.getAdded(Vector2(0, 10))
        enemy_distance = enemy.position.getSubtracted(Constants.BOTTOM_CENTER_POSITION).getMagnitude()
        font.render_to(w, font_line_1_location.toTuple(), "%.0f" % enemy_distance)
        font.render_to(w, font_line_2_location.toTuple(), enemy.name)
        if enemy.lockedOn:
            #enemy_distance = enemy.position.getSubtracted(Constants.BOTTOM_CENTER_POSITION).getMagnitude() 
            #bullet_velocity = Vector2.CreateNormalized(player_angle).scalarMultiply(player_muzzle_velocity)
            #velocity_tgt_sum = bullet_velocity.getAdded(enemy.velocity)
            #vtgtsum_normalized = velocity_tgt_sum.getNormalized()
            #scaledsum = vtgtsum_normalized.scalarMultiply(enemy_distance)
            #shouldAim = Constants.BOTTOM_CENTER_POSITION.getAdded(scaledsum)
            velocityScaled = enemy.velocity.scalarMultiply(0.75)
            factor = 0.1
            while factor < 0.9:
                subPoint = enemy.position.getAdded(velocityScaled.scalarMultiply(factor))
                util.alt_circle(w, self.LOCKED_COLOR, subPoint.toTuple(), 1, 1)
                factor += 0.2
            
            shouldAim = enemy.position.getAdded(velocityScaled)
            util.alt_circle(w, self.LOCKED_COLOR, shouldAim.toTuple(), 10, 1)
    
    def lock_nearest_enemy(self, mouse_ingame_pos):
        best_distance = 999999999
        best_enemy = None
        for enemy in enemies:
            dist = enemy.position.getSubtracted(mouse_ingame_pos).getMagnitude() 
            enemy.lockedOn = False
            if dist < best_distance:
                best_distance = dist
                best_enemy = enemy
        if best_distance == 999999999:
            return
        best_enemy.lockedOn = True
    
    def draw_reticle(self, w, pixelcoords):
        pygame.draw.circle(w, self.DEFAULT_COLOR, pixelcoords, 30, 1)
        pygame.draw.circle(w, self.DEFAULT_COLOR, pixelcoords, 2)
    
    def add_banner(self, msg, showtime):
        self.banner = [msg, time.time() + showtime]
        
  
class Enemy:
    position = None
    velocity = None
    acceleration = None
    radius = None
    hp = None
    name = None
    lockedOn = None
    
    def __init__(self, pos_x, pos_y, exit_velocity, exit_angle, radius, hp, name):
        self.position = Vector2(pos_x, pos_y)
        self.velocity = Vector2.CreateNormalized(exit_angle).scalarMultiply(exit_velocity)
        self.acceleration = Vector2(0, Constants.g)
        self.radius = radius
        self.hp = hp
        self.name = name
        self.lockedOn = False
        
    def updatePosition(self, dt):
        self.velocity.add(self.acceleration.scalarMultiply(dt))
        self.position.add(self.velocity.scalarMultiply(dt))
        
    def isOutsideBounds(self, lowerLeft, upperRight):
        if self.position.x < lowerLeft.x:
            return True
        if self.position.y < lowerLeft.y:
            return True
        if self.position.x > upperRight.x:
            return True
        if self.position.y > upperRight.y:
            return True
    
    def inflictDamage(self, dmg):
        self.hp -= dmg
    
    def isDead(self):
        return self.hp <= 0.0
    
    def __str__(self):
        return ("%s: Pos=%s Vel=%s HP=%.2f" % (self.name, self.position, self.velocity, self.hp))

w = pygame.display.set_mode([Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT])   
util = ScreenUtil(Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT, Constants.METERS_PER_PIXEL)
gamehud = GameHUD(util)
c = pygame.time.Clock()
pygame.mouse.set_visible(False)

projectiles = []
enemies = []

i = 0
while i < 4:
    enemies.append(Enemy(random.randint(0, 2000), 1900, 50, (math.pi * 5 / 4) + (random.random() * math.pi / 2), 50, 1, "ASTEROID"))
    i += 1

running = True
while running:
    # get mouse position and angle from center in terms of in-game arbitrary units.
    mx,my = pygame.mouse.get_pos()
    mouse_ingame_pos = util.to_game_coords(Vector2(mx, my))
    mouse_center_displacement = mouse_ingame_pos.getSubtracted(Constants.BOTTOM_CENTER_POSITION)
    theta = mouse_center_displacement.getAngle()
    
    # shoot a rod if mouse clicked. if quitting the game, stop the event loop.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            # add a rod to the list of projectiles, starting from the bottom center
            projectiles.append(Projectile(Constants.BOTTOM_CENTER_POSITION.x, Constants.BOTTOM_CENTER_POSITION.y, Constants.PLAYER_MUZZLE_SPEED, theta, 60, 10))
    
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        gamehud.lock_nearest_enemy(mouse_ingame_pos)
    
    # clear the screen.
    util.clear(w)
    
    # time step between frames for Riemann integration of velocity/displacement data.
    dt = c.get_time() / 1000.0
    
    # draw projectiles.
    for projectile in projectiles:
        if projectile.isOutsideBounds(Constants.LEFT_BOTTOM_POSITION, Constants.RIGHT_TOP_POSITION):
            gamehud.add_banner("[  MISS  ]", 1)
            projectiles.remove(projectile)
            continue
            
        enemyColliding = projectile.isColliding(enemies, dt)
        if enemyColliding != None:
            gamehud.add_banner("[  HIT  ]", 1)
            projectiles.remove(projectile)
            enemyColliding.inflictDamage(random.random() + 0.9)
            
        projectile.updatePosition(dt)
        util.draw_projectile(w, projectile)
        
    # draw enemies.
    for enemy in enemies:
        if enemy.position.y <= 0:
            enemies.remove(enemy)
            continue
        if enemy.isOutsideBounds(Constants.LEFT_BOTTOM_POSITION, Constants.RIGHT_TOP_POSITION):
            enemy.velocity.x = -enemy.velocity.x
            enemy.updatePosition(dt)
            continue
        if enemy.isDead():
            gamehud.add_banner("[  DESTROYED  ]", 2)
            enemies.remove(enemy)
            continue
        enemy.updatePosition(dt)
        util.draw_enemy(w, enemy)
        gamehud.draw_enemy_hud_info(w, enemy, Constants.PLAYER_MUZZLE_SPEED, theta)
        
    
    # draw turret
    util.rect(w, (128, 128, 128), Vector2(1200, 0), Vector2(1300, 100))
    util.line(w, (0, 0, 0), Constants.BOTTOM_CENTER_POSITION.toTuple(), Constants.BOTTOM_CENTER_POSITION.getAdded(mouse_center_displacement.getNormalized().scalarMultiply(200)).toTuple(), 20)
    
    # draw targeting reticle.
    gamehud.draw_reticle(w, (mx, my))
    
    # flip the screen and wait appropriately to maintain ~100FPS
    util.flip()
    c.tick(100)






# Turn in your Coding Exercise.
