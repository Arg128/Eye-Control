# ...existing code...
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2
import cv2
import pygame
import mouse
import numpy as np
import os

gestures = EyeGestures_v2()
cap = VideoCapture(0)
calibrate = True

x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)

calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map, context="eye_Tracker")
gestures.setClassicalImpact(2)
gestures.setFixation(1.0)

iterator = 0
prev_x = 0
prev_y = 0

# Pygame UI
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v2 - Calibración")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)

# colores
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "calibration_model_eye_tracker.pkl")
max_points = 35
saved = False

running = True
while running:
    # eventos pygame
    for pyevent in pygame.event.get():
        if pyevent.type == pygame.QUIT:
            running = False
        elif pyevent.type == pygame.KEYDOWN:
            if pyevent.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    # leer cámara (una sola vez)
    ret, frame = cap.read()
    if not ret or frame is None:
        # evita ValueError de np.rot90 si falla la cámara
        continue

    # convertir a RGB (el ejemplo original usaba RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # decide si estamos en fase de calibración
    calibrate = (iterator <= max_points)

    # llamada única a step con el frame correcto
    event, calibration = gestures.step(frame_rgb, calibrate, screen_width, screen_height, context="eye_Tracker")

    # preparar imagen para mostrar en Pygame
    try:
        display = np.rot90(frame_rgb)
        surf = pygame.surfarray.make_surface(display)
        surf = pygame.transform.scale(surf, (400, 400))
    except Exception:
        surf = None

    screen.fill((0, 0, 0))

    if event is None and calibration is None:
        # sin datos válidos este frame
        if surf is not None:
            screen.blit(surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

    # mover mouse si hay evento de tracking (cuando no se está dibujando calibración)
    if event and not calibrate:
        cursor_x, cursor_y = event.point[0], event.point[1]
        mouse.move(cursor_x, cursor_y, absolute=True, duration=0.01)

    # dibujado UI
    if surf is not None:
        screen.blit(surf, (0, 0))

    my_font = pygame.font.SysFont('Comic Sans MS', 30)
    if event is not None:
        text_surface = my_font.render(f'fix:{event.fixation:.2f}', False, (0, 0, 0))
        screen.blit(text_surface, (0, 0))

    if calibrate and calibration is not None:
        # avanzamos contador cuando el punto cambia
        if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
            iterator += 1
            prev_x, prev_y = calibration.point[0], calibration.point[1]
        calibration_radius = max(1, int(calibration.acceptance_radius) - 7)
        fit_point = (int(calibration.point[0]), int(calibration.point[1]))
        pygame.draw.circle(screen, GREEN, fit_point, calibration_radius)
        text_surface = bold_font.render(f"{iterator}/{max_points}", True, WHITE)
        text_square = text_surface.get_rect(center=calibration.point)
        screen.blit(text_surface, text_square)
    else:
        # mostrar el punto estimado en modo tracking
        if event is not None:
            pygame.draw.circle(screen, RED if gestures.whichAlgorithm(context="eye_Tracker") == "Ridge" else BLUE, (int(event.point[0]), int(event.point[1])), 20)
            alg_text = my_font.render(gestures.whichAlgorithm(context="eye_Tracker"), False, (0, 0, 0))
            screen.blit(alg_text, (int(event.point[0]), int(event.point[1])))

    pygame.display.flip()

    # cuando terminamos la calibración, guardamos modelo y salimos
    if iterator > max_points and not saved:
        model_bytes = gestures.saveModel(context="eye_Tracker")
        if model_bytes:
            with open(MODEL_PATH, "wb") as f:
                f.write(model_bytes)
        saved = True
        # cerramos la UI y salimos del loop para dejar solo tracking en otro script
        pygame.quit()
        running = False
        break

    clock.tick(60)

# limpieza
try:
    cap.release()
except Exception:
    pass
pygame.quit()
# ...existing code...