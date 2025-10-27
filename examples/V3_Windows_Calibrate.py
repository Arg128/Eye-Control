import os
import sys
import warnings
import cv2
import numpy as np
import pygame
import mouse
import ctypes
import argparse

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

context_tag = "eye_Tracker_v3"

# init gestures (try passing calibration_radius if supported)
try:
    gestures = EyeGestures_v3(calibration_radius=900)
except TypeError:
    gestures = EyeGestures_v3()

# --- helper: open video source robustly and set resolution ---
def open_video_source(source, width=None, height=None, fps=None):
    # source: int index or path/URL
    try:
        src = int(source)
    except Exception:
        src = source
    cap_local = VideoCapture(src)
    if width:
        try:
            cap_local.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        except Exception:
            pass
    if height:
        try:
            cap_local.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
        except Exception:
            pass
    if fps:
        try:
            cap_local.set(cv2.CAP_PROP_FPS, float(fps))
        except Exception:
            pass
    return cap_local

# --- helper: ensure a face is detected in at least `threshold` fraction of `frames` frames ---
def ensure_face_present(cap_obj, frames=30, threshold=0.8, min_face_area_ratio=0.01):
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    detections = 0
    total = 0
    tstart = pygame.time.get_ticks()
    while total < frames:
        ret, f = cap_obj.read()
        if not ret or f is None:
            continue
        gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
        total += 1
        if len(faces) > 0:
            # check largest face area ratio to avoid tiny false positives
            (x,y,w,h) = max(faces, key=lambda r: r[2]*r[3])
            area_ratio = (w*h) / float(f.shape[0]*f.shape[1])
            if area_ratio >= min_face_area_ratio:
                detections += 1
    frac = detections / float(total) if total > 0 else 0.0
    return frac >= threshold, frac, detections, total

# --- parse optional CLI args for camera source / resolution ---
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--source", default="0", help="camera index or video path (default 0)")
parser.add_argument("--width", type=int, default=None)
parser.add_argument("--height", type=int, default=None)
parser.add_argument("--fps", type=float, default=None)
args, _ = parser.parse_known_args()

# camera
cap = open_video_source(args.source, width=args.width, height=args.height, fps=args.fps)

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
#   max_points = 70
saved = False
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
    #   frame_rgb = np.flip(frame_rgb, axis=1)
    calibrate = (iterator <= max_points)

    # single step call
    event, calibration = gestures.step(frame_rgb, calibrate, screen_width, screen_height, context=context_tag)
    # prepare small preview
    surf = None
    """     try:
        frame_rgb = np.rot90(frame_rgb)
        preview = frame_rgb
        surf = pygame.surfarray.make_surface(preview)
        surf = pygame.transform.scale(surf, (200, 200))
    except Exception:
        surf = None """

    screen.fill((0, 0, 0))
    if surf is not None:
        #   screen.blit(surf, (10, 10))
                # Display frame on Pygame screen
        """         screen.blit(
            pygame.surfarray.make_surface(
                np.rot90(event.sub_frame)
            ),
            (0, 0)
        ) """

    # no valid data this frame
    if event is None and calibration is None:
        pygame.display.flip()
        clock.tick(60)
        continue

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
        pygame.draw.circle(screen, (0, 255, 0), (int(calibration.point[0]), int(calibration.point[1])), cal_rad)
        txt = bold_font.render(f"{iterator}/{max_points} \n {gestures.whichAlgorithm(context_tag)}", True, (255, 255, 255))
        rect = txt.get_rect(center=calibration.point)
        screen.blit(txt, rect)
            # --- reduce calibration radii gradually (coarse -> fine) ---
                # gestures.clb[context_tag] existe en muchas implementaciones
        try:
            if (iterator % 7) == 0 and CHANGERADIO:  # cada 2 puntos ajusta radios
                CHANGERADIO = False
                clb_dict = getattr(gestures, "clb", None)
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
    sys.exit("Salida del todo el programa python")
    pygame.quit()
except Exception:
    warnings.warn("No se pudo cerrar de forma correcta")

print("Calibración finalizada. Modelo guardado en:", MODEL_PATH)