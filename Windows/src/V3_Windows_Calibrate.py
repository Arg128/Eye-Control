import argparse
import os
import sys
import warnings
import cv2
import numpy as np
import pygame
import mouse
import ctypes

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

from check import ensure_face_present, open_video_source

context_tag = "eye_Tracker_v3"

# init gestures (try passing calibration_radius if supported)
try:
    gestures = EyeGestures_v3(calibration_radius=70)
except TypeError:
    gestures = EyeGestures_v3()



# --- parse optional CLI args for camera source / resolution ---

# camera
cap = open_video_source(0)
# camera
#cap = VideoCapture(0)

# build calibration map (normalized 0..1)
x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)
calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map, context=context_tag)

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

import sys    
print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
#   sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

#   from src import points
print(sys.argv[1:][0])
print(f"Recibí los argumentos: {(sys.argv[1:])}")
max_points = int(sys.argv[1:][0])
saved = bool(sys.argv[1:][1])
running = True

CHANGERADIO = True

print("Quick bias calibration: mira al centro de la pantalla y pulsa Enter")
#input("Pulsa Enter cuando estés listo...")
# captura predicciones durante 2 segundos o hasta N muestras válidas


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
    frame_rgb = np.rot90(frame_rgb)
    #   frame_rgb = np.flip(frame_rgb, axis=1)
    calibrate = (iterator <= max_points)

    # single step call
    
    event, calibration = gestures.step(frame_rgb, calibrate, screen_width, screen_height, context=context_tag)
    # prepare small preview
        # no valid data this frame
    if event is None and calibration is None:
        pygame.display.flip()
        clock.tick(60)
        continue

    surf = None
    try:
        surf = pygame.surfarray.make_surface(frame_rgb)
        surf = pygame.transform.scale(surf, (400, 400))
    except Exception:
        surf = None

    screen.fill((0, 0, 0))
    if surf is not None:
        ref_image = np.flip(event.sub_frame, axis=0)
        screen.blit(
            pygame.surfarray.make_surface(
                event.sub_frame
            ),
            (screen_width/2 - 200, 0)
        )
        #   screen.blit(surf, (10, 10))

    # mover mouse si no hay evento de tracking (cuando se está dibujando calibración)
    if event and calibrate:
        cursor_x, cursor_y = event.point[0], event.point[1]
        mouse.move(cursor_x, cursor_y, absolute=True, duration=0.01)

    if calibration is not None and calibrate:
        if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
            iterator += 1
            prev_x, prev_y = calibration.point[0], calibration.point[1]
            CHANGERADIO = True
            ##
        cal_rad = max(1, int(calibration.acceptance_radius) - 8)
        pygame.draw.circle(screen, (0, 255, (iterator * 7)%256), (int(calibration.point[0]), int(calibration.point[1])), cal_rad)
        txt = bold_font.render(f"{iterator}/{max_points} \n {gestures.whichAlgorithm(context_tag)}", True, (255, 255, 255))
        rect = txt.get_rect(center=calibration.point)
        screen.blit(txt, rect)
            # --- reduce calibration radii gradually (coarse -> fine) ---
                # gestures.clb[context_tag] existe en muchas implementaciones
        try:
            clb_dict = getattr(gestures, "clb", None)
            if (iterator % 7) == 0 and CHANGERADIO and clb_dict[context_tag].calibration_radius > 70:  # cada 2 puntos ajusta radios
                CHANGERADIO = False
                if clb_dict and context_tag in clb_dict:
                    clb_obj = clb_dict[context_tag]
                    print(clb_obj.calibration_radius)
                    # parámetros: factor de reducción y límite mínimo
                    reduction_factor = 0.90   # reducir 10% cada punto completado
                    min_cal_radius = 50       # píxeles (ajusta según pantalla)
                    min_acc_radius = 10
                    # actualizar radios (si las propiedades existen)
                    if hasattr(clb_obj, "calibration_radius"):
                        clb_obj.calibration_radius = max(min_cal_radius,
                                                            int(clb_obj.calibration_radius * reduction_factor))
                    if hasattr(clb_obj, "acceptance_radius"):
                        clb_obj.acceptance_radius = max(min_acc_radius,
                                                        int(clb_obj.acceptance_radius * reduction_factor))
        except Exception:
            pass
        """     # during calibration show target and progress
    if calibration is not None and calibrate:
        if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
            iterator += 1
            prev_x, prev_y = calibration.point[0], calibration.point[1]
        cal_rad = max(1, int(calibration.acceptance_radius) - 8)
        pygame.draw.circle(screen, (0, 255, 0), (int(calibration.point[0]), int(calibration.point[1])), cal_rad)
        txt = bold_font.render(f"{iterator}/{max_points}", True, (255, 255, 255))
        rect = txt.get_rect(center=calibration.point)
        screen.blit(txt, rect) """
        #BETA
        """         clb_obj = clb_dict[context_tag]
        # parámetros: factor de reducción y límite mínimo
        reduction_factor = 0.90   # reducir 10% cada punto completado
        min_cal_radius = 50       # píxeles (ajusta según pantalla)
        min_acc_radius = 10
        # actualizar radios (si las propiedades existen)
        if hasattr(clb_obj, "calibration_radius"):
            clb_obj.calibration_radius = max(min_cal_radius,
                                                int(clb_obj.calibration_radius * reduction_factor))
        if hasattr(clb_obj, "acceptance_radius"):
            clb_obj.acceptance_radius = max(min_acc_radius,
                                            int(clb_obj.acceptance_radius * reduction_factor)) """
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
        ##  pygame.quit()
        ##  running = False
        ##  break

    clock.tick(60)

# cleanup
try:
    cap.close()
        # before calibrating, require a stable face
    cap = open_video_source(0)
    screen.blit(pygame.font.SysFont(None, 24).render("Comprobando rostro estable...", True, (0, 0, 0)), (screen_width/2 - 200, screen_height/2))
    print("Comprobando presencia de rostro estable (espera...)")
    ok, frac, dets, tot = ensure_face_present(cap, frames=30, threshold=0.8)
    print(f"Rostro detectado en {dets}/{tot} frames -> frac={frac:.2f}")
    if not ok:
        print("No se detecta rostro suficientemente estable (>0.8). Mejora iluminación/posición o cambia la fuente con --source.")
    print("Calibración finalizada. Modelo guardado en:", MODEL_PATH)
    cap.close()
    pygame.quit()
    sys.exit("Salida del todo el programa python")
except Exception:
    warnings.warn("No se pudo cerrar de forma correcta")
