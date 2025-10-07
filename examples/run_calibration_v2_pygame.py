import os
import sys
import cv2
import pygame
import numpy as np

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v2 calibration (pygame)")
font_size = 36
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures import EyeGestures_v2
from eyeGestures.utils import VideoCapture

gestures = EyeGestures_v2(calibration_radius=1000)
cap = VideoCapture(0)

# Build calibration map (normalizado 0..1)
x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)
calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map, context="v2calib")
gestures.setFixation(1.0)

n_points = min(len(calibration_map), 50)
iterator = 0
prev_pt = (-1, -1)

# Colors
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255,255,255)
BLACK = (0,0,0)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.flip(frame, axis=1)

    calibrate = (iterator <= n_points)
    gevent, cevent = gestures.step(frame, calibrate, screen_width, screen_height, context="v2calib")

    screen.fill(BLACK)

    # Show camera subframe if available
    if gevent is not None and gevent.sub_frame is not None:
        sf = np.rot90(gevent.sub_frame)
        surf = pygame.surfarray.make_surface(sf)
        surf = pygame.transform.scale(surf, (400, 400))
        screen.blit(surf, (0,0))

    # Draw calibration circle and progress
    if cevent is not None:
        pt = tuple(map(int, cevent.point))
        pygame.draw.circle(screen, BLUE, pt, int(cevent.acceptance_radius))
        text_surface = bold_font.render(f"{iterator}/{n_points}", True, WHITE)
        text_rect = text_surface.get_rect(center=pt)
        screen.blit(text_surface, text_rect)
        # Count progress when point moves
        if calibrate:
            if pt != prev_pt:
                iterator += 1
                prev_pt = pt

    # Draw algorithm name
    algo = gestures.whichAlgorithm(context="v2calib")
    algo_surface = pygame.font.SysFont('Arial', 24).render(algo, True, WHITE)
    screen.blit(algo_surface, (10, screen_height - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
