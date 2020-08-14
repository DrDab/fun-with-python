import math
import pygame
pygame.init()

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
MAX_FPS = 120

WAVE_SPEED = 10
METERS_PER_PIXEL = 10 / SCREEN_HEIGHT
INTENSITY_MAX = 1
WAVELENGTH = 1.2

def wave_amplitude(x, t):
    if x > WAVE_SPEED * t:
        return 0.0
    return INTENSITY_MAX * math.sin((2 * math.pi * x / WAVELENGTH) - (WAVE_SPEED * t))

w = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
c = pygame.time.Clock()

center_x = SCREEN_WIDTH / 2
center_y = SCREEN_HEIGHT / 2

time = 0.0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    w.fill((0, 0, 0))
    for i in range(0, 80):
        x_px = i * 10.0
        for j in range(0, 80):
            y_px = j * 10.0
            d = math.hypot(center_x - x_px, center_y - y_px) * METERS_PER_PIXEL
            a = wave_amplitude(d, time)
            grayscale = int(255 * (a + 1) / 2)
            pygame.draw.circle(w, (grayscale, grayscale, grayscale), (int(x_px), int(y_px)), 5)


    time += c.get_time() / 1000.0
    pygame.display.flip()
    c.tick(MAX_FPS)
