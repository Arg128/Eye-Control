import argparse
import os
import sys
import warnings
import cv2
import numpy as np
import pygame
import mouse
import ctypes
import time  # wait a bit for camera to be ready
import win32con
import win32gui
import pickle

import win32api
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3
from sklearn.linear_model import Ridge
from calib_io import save_calibration_csv, save_calibration_npz, save_sklearn_model
import keyboard

from check import ensure_face_present, open_video_source

context_tag = "eye_Tracker_v3"

radio = int(sys.argv[1:][2])
# init gestures (try passing calibration_radius if supported)
try:
    gestures = EyeGestures_v3(calibration_radius=radio)
except TypeError:
    gestures = EyeGestures_v3()



# --- parse optional CLI args for camera source / resolution ---

# camera

time.sleep(12)  # wait a bit for camera to be ready
cap = open_video_source(0)


# build calibration map (normalized 0..1)
x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)
calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map, context=context_tag)


if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
    except Exception:
        pass


screen_width = int(sys.argv[1:][3])
screen_height = int(sys.argv[1:][4])

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((screen_width, screen_height))
hwnd = pygame.display.get_wm_info()["window"]

# Getting information of the current active window
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(
                       hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 128), 0, win32con.LWA_COLORKEY)
# This will set the opacity and transparency color key of a layered window
font = pygame.font.SysFont("Times New Roman", 54)
# declare the size and font of the text for the window
text = []
# Declaring the array for storing the text
text.append((font.render("Press Ctrl + Q to Escape", 0, (255, 100, 100)), (20, 250)))
pygame.display.set_caption("EyeGestures v3 - Calibración")
clock = pygame.time.Clock()
bold_font = pygame.font.Font(None, 48)
bold_font.set_bold(True)

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

iter = 0
MAX_ITER = 100
print("Quick bias calibration: mira al centro de la pantalla y pulsa Enter")
#input("Pulsa Enter cuando estés listo...")
# captura predicciones durante 2 segundos o hasta N muestras válidas


while running:
         # Transparent background
    screen.fill((255,0,128)) 
            # stop via keyboard (non-blocking check)
    if keyboard.is_pressed('ctrl'):
        print("Ctrl pressed -> stopping.")
        break
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    if (MAX_ITER < iter):
        break
    try:
        ret, frame = cap.read()
        print("SHAPE",frame.shape)
    except Exception:
        iter += 1
        print("Warning: unable to read from camera")
        screen.blit(pygame.font.SysFont(None, 24).render("Warning: unable to read from camera", True, (255, 255, 255)), (10, 10))
        continue
    print("One")
    if not ret or frame is None:
        continue
    print("Two")
    try:
        if frame is not None:
            print("Three")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = np.rot90(frame_rgb)
    except Exception as ex:
        print("Three - Exception")
        print("Error converting frame to RGB:", ex)
        iter += 1
        screen.blit(pygame.font.SysFont(None, 24).render("Warning: unable to process camera frame", True, (255, 255, 255)), (10, 10))
        clock.tick(60)
        continue
    #   frame_rgb = np.flip(frame_rgb, axis=1)
    calibrate = (iterator <= max_points)

    # single step call
    try:
        print("Four")
        event, calibration = gestures.step(frame_rgb, calibrate, screen_width, screen_height, context=context_tag)
    except Exception as ex:
        print("Error during gestures.step():", ex)
        screen.blit(pygame.font.SysFont(None, 24).render("Warning: unable to read gestures", True, (255, 255, 255)), (10, 10))
        iter += 1
        clock.tick(60)
        continue
    # prepare small preview
        # no valid data this frame
    if event is None and calibration is None:
        print("Five")
        pygame.display.flip()
        clock.tick(60)
        continue

    print("Six")
    surf = None
    try:
        surf = pygame.surfarray.make_surface(frame_rgb)
        surf = pygame.transform.scale(surf, (210, 210))
    except Exception:
        surf = None

    #   screen.fill((0, 0, 0))
    
    #   APLICALO CON ROSTRO
    """     if surf is not None:
        ref_image = np.flip(event.sub_frame, axis=0)
        screen.blit(
            pygame.surfarray.make_surface(
                event.sub_frame
            ),
            (screen_width/2 - 200, 0)
        ) """
    screen.blit(surf, (0, 10))

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
            print("Error ajustando radios de calibración")
            iter += 1
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
        ## model_bytes = gestures.saveModel(context=context_tag)
        ## if model_bytes:
        ##    with open(MODEL_PATH, "wb") as f:
        ##        f.write(model_bytes)
        ##saved = True
        ##  pygame.quit()
        ##  running = False
        ##  break

    clock.tick(60)
if iterator >= max_points and saved:
        out_dir = os.path.join(os.path.dirname(__file__), "saved")
        tmp_path = os.path.join(out_dir, "my_file_v3.bin") + ".tmp"
        os.makedirs(out_dir, exist_ok=True)
        clb_dict = getattr(gestures, "clb", None)
        clb = clb_dict[context_tag] 
        # clb es tu calibrador con atributos X, Y_x, Y_y y reg_x/reg_y/scaler si existen
        #npz_path = os.path.join(os.path.dirname(__file__), "saved", "calib_v3_data.npz")
        dataNuevo = gestures.saveModel(context=context_tag)
        print(dataNuevo)
        print(clb.X)
        print(clb.Y_y)
        print(clb.Y_x)
        time.sleep(14)
        if dataNuevo:
                # ensure we have raw bytes
            if not isinstance(dataNuevo, (bytes, bytearray)):
                print("Esto es un pickle aaAaAAAA")
                data_bytes = pickle.dumps(dataNuevo)
            else:
                print("Yo espero de que caigas justo aquí")
                data_bytes = bytes(dataNuevo)

            # atomic write with flush+fsync
            with open(tmp_path, "wb") as f:
                f.write(data_bytes)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, os.path.join(out_dir, "my_file_v3.bin"))
            #with open(os.path.join(out_dir, 'my_file_v3.bin'), 'wb') as file:
            #    file.write(dataNuevo)
            #file.close()

        #   save_calibration_npz(npz_path, clb.X, clb.Y_x, clb.Y_y, meta={"screen": (1920, 1080)})

        # opcional: guardar también los modelos entrenados
        #   save_sklearn_model(os.path.join(os.path.dirname(__file__), "saved", "reg_x.joblib"), clb.reg_x)
        #   save_sklearn_model(os.path.join(os.path.dirname(__file__), "saved", "reg_y.joblib"), clb.reg_y)
        save_calibration_csv(os.path.join(os.path.dirname(__file__), "saved", "calib_v3_data.csv"), clb.X, clb.Y_x, clb.Y_y, header=None)
        if hasattr(clb, "scaler") and clb.scaler is not None:
            save_sklearn_model(os.path.join(out_dir, "scaler.joblib"), clb.scaler)

else:
    time.sleep(1)
    print("Calibracion mala,")
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
    print("Calibración finalizada. Modelo guardado en:")
    cap.close()
    pygame.quit()
    sys.exit("Salida del todo el programa python")
except Exception:
    warnings.warn("No se pudo cerrar de forma correcta")
