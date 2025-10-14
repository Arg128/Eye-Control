import os
import sys
import cv2
import numpy as np
import pygame
import mouse
import ctypes

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

context_tag = "eye_Tracker_v3"

# init gestures (try passing calibration_radius if supported)
try:
    gestures = EyeGestures_v3(calibration_radius=900)
except TypeError:
    gestures = EyeGestures_v3()

# camera
cap = VideoCapture(0)

# build calibration map (normalized 0..1)
x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)
calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map, context=context_tag)
gestures.setFixation(1.0)

# Try to ensure context exists (avoid KeyError on step)
if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
    except Exception:
        pass

# Screen resolution (Windows)
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Pygame UI
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v3 - Calibración")
clock = pygame.time.Clock()
bold_font = pygame.font.Font(None, 48)
bold_font.set_bold(True)

MODEL_DIR = os.path.join(os.path.dirname(__file__), ".pkl")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "calibration_model_v3.pkl")

iterator = 0
prev_x = prev_y = 0
max_points = min(len(calibration_map), 50)
saved = False
running = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    calibrate = (iterator <= max_points)

    # single step call
    event, calibration = gestures.step(frame_rgb, calibrate, screen_width, screen_height, context=context_tag)

    # prepare small preview
    surf = None
    try:
        preview = np.rot90(frame_rgb)
        surf = pygame.surfarray.make_surface(preview)
        surf = pygame.transform.scale(surf, (400, 400))
    except Exception:
        surf = None

    screen.fill((0, 0, 0))
    if surf is not None:
        screen.blit(surf, (10, 10))

    # no valid data this frame
    if event is None and calibration is None:
        pygame.display.flip()
        clock.tick(60)
        continue

    # during calibration show target and progress
    if calibration is not None and calibrate:
        if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
            iterator += 1
            prev_x, prev_y = calibration.point[0], calibration.point[1]
        cal_rad = max(1, int(calibration.acceptance_radius) - 8)
        pygame.draw.circle(screen, (0, 255, 0), (int(calibration.point[0]), int(calibration.point[1])), cal_rad)
        txt = bold_font.render(f"{iterator}/{max_points}", True, (255, 255, 255))
        rect = txt.get_rect(center=calibration.point)
        screen.blit(txt, rect)
    else:
        # tracking: move mouse using predicted point
        if event is not None:
            px, py = int(event.point[0]), int(event.point[1])
            mouse.move(px, py, absolute=True, duration=0.01)
            alg = gestures.whichAlgorithm(context=context_tag) if hasattr(gestures, "whichAlgorithm") else "?"
            pygame.draw.circle(screen, (255, 0, 0) if alg == "Ridge" else (100, 0, 255), (px, py), 18)
            screen.blit(pygame.font.SysFont(None, 24).render(alg, True, (0, 0, 0)), (px + 10, py + 10))

    pygame.display.flip()

    # once finished save model and exit (close pygame to allow headless tracking script)
    if iterator > max_points and not saved:
        model_bytes = gestures.saveModel(context=context_tag)
        if model_bytes:
            with open(MODEL_PATH, "wb") as f:
                f.write(model_bytes)
        saved = True
        pygame.quit()
        running = False
        break

    clock.tick(60)

# cleanup
try:
    cap.release()
except Exception:
    pass
pygame.quit()
print("Calibración finalizada. Modelo guardado en:", MODEL_PATH)