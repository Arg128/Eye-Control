# ...existing code...
import os
import sys
import time
import warnings
import subprocess
import cv2
import ctypes
import mouse
import numpy as np
import keyboard
import win32con
import win32api
import win32gui
from screeninfo import get_monitors

import pygame
from collections import deque
import itertools

from eyeGestures import EyeGestures_v3
from eyeGestures.utils import VideoCapture
# archivo "check" que define ensure_face_present / open_video_source en tu repo
from check import ensure_face_present, open_video_source
from calib_io import load_calibration_npz, load_sklearn_model, save_calibration_csv
from sklearn.linear_model import Ridge
from generate_stats import make_heatmap, save_heatmap_png
from heatmap import Heatmap

# --- config ---
context_tag = "eye_Tracker_v3"

screen_w = int(sys.argv[1:][0])
screen_h = int(sys.argv[1:][1])

""" # model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), ".pkl", "calibration_model_v3.pkl")
if not os.path.exists(MODEL_PATH):
    print("No model found. Run run_calibration_v3_pygame.py first.")
    sys.exit(1) """
x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)
calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
# load gestures & model
gestures = EyeGestures_v3()
xs = deque(maxlen=20000)
ys = deque(maxlen=20000)

if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
    except Exception:
        pass
else:
    print("No hay nada")
    gestures.uploadCalibrationMap(calibration_map, context=context_tag)

#   print(f"Loading model from {MODEL_PATH}...")
print("New loader '.npz' file")
#   MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved", "my_file_v3.pkl")
# intento cargar joblib primero
saved = os.path.join(os.path.dirname(__file__), "saved")

""" X, Yx, Yy, meta = load_calibration_npz(os.path.join(saved, "calib_v3_data.npz"))
reg_x = Ridge(alpha=1.0).fit(X, Yx.ravel())
reg_y = Ridge(alpha=1.0).fit(X, Yy.ravel()) """
#   print("Regressors reentrenados desde NPZ")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved", "my_file_v3.bin")
loaded_model_ok = False
""" if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            blob = f.read()
        print("Leídos", len(blob), "bytes desde", MODEL_PATH)
        print(blob)
        # 1) intentar pasar blob directamente (si saveModel devolvió bytes)
        try:
            gestures.loadModel(blob, context=context_tag)
            loaded_model_ok = True
            print("Modelo cargado pasando bytes a gestures.loadModel()")
        except Exception as e_bytes:
            # 2) intentar unpickle y pasar el objeto resultante
            try:
                import pickle
                obj = pickle.loads(blob)
                gestures.loadModel(obj, context=context_tag)
                loaded_model_ok = True
                print("Modelo cargado después de pickle.loads()")
            except Exception as e_pickle:
                print("No se pudo cargar modelo (bytes):", e_bytes, " ; (pickle):", e_pickle)
    except Exception as e:
        print("Error leyendo MODEL_PATH:", e)
else:
    print("Modelo no encontrado en", MODEL_PATH)
 """
time.sleep(7)
try:
    with open(MODEL_PATH, 'rb') as file:
        data = file.read()
    gestures.loadModel(data, context=context_tag)
    file.close()
except Exception as e:
    print("No se pudo cargar el modelo desde el pickle binario:")
    print(e)
    time.sleep(7)
""" try:
    with open(MODEL_PATH, "rb") as f:
        data = f.read()
    dataNuevo = gestures.loadModel(MODEL_PATH, context=context_tag)
except Exception as e:
    print("No se pudo cargar el modelo desde pickle:", e)
 """

# camera: request a stable resolution similar to calibration (adjust if needed)
CAP_WIDTH = 1280
CAP_HEIGHT = 720
#   print(f"Opening camera with resolution {CAP_WIDTH}x{CAP_HEIGHT}...")
cap = open_video_source(0)
""" try:
    cap.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(CAP_WIDTH))
    cap.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(CAP_HEIGHT))
except Exception:
    pass """
# ...insert after models load...

# --- diagnostics & robust attach of regressors/scaler ---

# ensure camera resolution applied to the real cv2 capture object
""" try:
    real_cap = getattr(cap, "cap", cap)
    real_cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(CAP_WIDTH))
    real_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(CAP_HEIGHT))
    # read one frame to confirm
    ret0, f0 = real_cap.read()
    if ret0 and f0 is not None:
        print("confirm frame.shape after set:", f0.shape)
    else:
        print("warning: no frame after setting resolution; got ret0=", ret0)
except Exception as e:
    print("warning setting capture resolution:", e)
 """
""" 
clb_dict = getattr(gestures, "clb", None)
clb = clb_dict.get(context_tag, None)
clb.reg_x = reg_x
clb.reg_y = reg_y
clb.scaler = scaler

 """
# try to get device FPS; fallback to 60
cap_fps = cap.cap.get(cv2.CAP_PROP_FPS)
try:
    target_fps = int(cap_fps) if cap_fps and cap_fps > 0 else 60
except Exception:
    target_fps = 60

print(target_fps)
frame_time = 1.0 / max(1, target_fps)
print(f"Target FPS for tracking: {target_fps} (frame_time={frame_time:.3f}s)")

# preproc flags (must match what you used during calibration)
APPLY_ROT90 = True        # calibrate used np.rot90(frame_rgb)
MIRROR_X = False          # set True if data is mirrored
MAX_ITER = 100
# safety: small debug prints for first frames
_debug_frames = 40
iter = 0
print("Starting V3 tracking loop. Press (Ctrl) to stop.")
stop = False

# --- after initialization and flags (APPLY_ROT90, MIRROR_X, frame_time, etc.) ---

# Helper: get a usable cap object (wrapper vs raw cv2 capture)
_cap = cap
if not hasattr(_cap, "read") and hasattr(_cap, "cap"):
    _cap = _cap.cap

_debug_frames = 20
iter_count = 0

print("Starting V3 tracking loop. Press Ctrl to stop.")

clock = pygame.time.Clock()
counter = 0
counter2 = 0
MAX = 1000
#Pygame UI
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((screen_w, screen_h))
hwnd = pygame.display.get_wm_info()["window"]

# Getting information of the current active window
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(
                       hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 128), 0, win32con.LWA_COLORKEY)
try:
    while True:
        # stop via keyboard (non-blocking check)
        screen.fill((255, 0, 128)) 
        t_now = time.perf_counter()
        if keyboard.is_pressed('ctrl'):
            print("Ctrl pressed -> stopping.")
            break
        # read frame robustly
        try:
            ret, frame = _cap.read()
        except Exception:
            # fallback if wrapper uses .read() differently
            try:
                ret, frame = cap.read()
            except Exception:
                ret, frame = False, None

        if not ret or frame is None:
            time.sleep(frame_time)
            iter_count += 1
            if iter_count > MAX_ITER:
                print("Max iterations reached without valid frames.")
                break
            clock.tick(60)
            continue

        # debug: show camera frame size first frames
        if _debug_frames > 0:
            print("camera frame.shape:", frame.shape)
            _debug_frames -= 1

        # preprocessing MUST match calibration
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if APPLY_ROT90:
            frame_rgb = np.rot90(frame_rgb)
        if MIRROR_X:
            frame_rgb = np.flip(frame_rgb, axis=1)

        # call gesture step
        try:
            evt, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        except Exception as ex:
            warnings.warn(f"gestures.step() error: {ex}")
            clock.tick(60)
            continue

        # validate evt and point
        if evt is None or getattr(evt, "point", None) is None:
            # optionally debug
            # print("No event or point")
            clock.tick(60)
            continue

        """ raw = np.asarray(evt.point, dtype=float).flatten()
        if raw.size < 2 or np.any(np.isnan(raw)) or np.any(np.isinf(raw)):
            print("Invalid evt.point:", raw)
            time.sleep(frame_time)
            continue 
        """

        """
         # Heuristics to convert raw -> screen pixels:
        # - If values look normalized (all in [-0.2..1.2]) treat as [0..1] and scale.
        # - Otherwise, if values are small (< screen dims) assume already pixels.
        max_abs = np.max(np.abs(raw))
        if np.all((raw >= -0.2) & (raw <= 1.2)):
            # normalized coordinates
            px = raw[0] * screen_w
            py = raw[1] * screen_h
        elif max_abs < max(screen_w, screen_h) * 1.05:
            # already in pixel coords (within screen range)
            px, py = raw[0], raw[1]
        else:
            # extreme out-of-bounds: try mapping from camera frame coords as fallback
            cam_h, cam_w = frame.shape[:2]
            # if raw seems in camera coordinates range, scale to screen
            if (0 <= raw[0] <= cam_w*1.5) and (0 <= raw[1] <= cam_h*1.5):
                px = (raw[0] / float(cam_w)) * screen_w
                py = (raw[1] / float(cam_h)) * screen_h
            else:
                # last resort: clip to center of screen to avoid erratic moves
                print("evt.point out-of-bounds, raw:", raw)
                print("SHAPE",frame.shape)
                print(evt.point)
                px, py = screen_w//2, screen_h//2

        # final sanitize and apply mirror if needed
        if MIRROR_X:
            px = screen_w - px 
        """

        # clip and cast to int
        #   x = int(np.clip(px, 0, screen_w - 1))
        #   y = int(np.clip(py, 0, screen_h - 1))
        x, y = evt.point[0], evt.point[1]
        print(evt.point)
            
        # move mouse safely
        try:
            x = abs(x)
            y = abs(y)
            y = screen_h if y > screen_h else y
            x = screen_w if x > screen_w else x
            mouse.move(x, y, absolute=True, duration=0)

            """             print(counter)
            print(counter2)
            if (counter < MAX):
                counter += 1
                xs.append(evt.point[0])
                ys.append(evt.point[1])
            else:
                counter2 += 1
                if (counter2 > MAX):
                    counter = 0
                    counter2 = 0 """
            # time throttle
            should_append = False
            if not should_append:
                if (t_now - globals().get('_last_app_time', 0.0)) >= 0.016:
                    should_append = True
            if should_append:
                xs.append(evt.point[0])
                ys.append(evt.point[1])
                globals()['_last_app_time'] = t_now
            
        except Exception as e:
            warnings.warn(f"mouse.move error: {e}")
            clock.tick(60)

        # optional debug print (limited)
        """         
            if iter_count < 10:
            print(f"raw={raw} -> px/py=({px:.1f},{py:.1f}) -> clipped=({x},{y})") """

        # rate control
        clock.tick(60)
        pygame.display.flip()
        #   iter_count += 1

        

except KeyboardInterrupt as e:
    time.sleep(7)
    print(e)
    print("Tracking interrupted by user.")
finally:
    try:
        if hasattr(_cap, "release"):
            _cap.release()
        elif hasattr(cap, "release"):
            cap.release()
    except Exception:
        pass

    from generate_stats import make_heatmap, save_heatmap_png, save_report_pdf
    from calib_io import save_calibration_csv
    #   h_map = Heatmap(screen_h, screen_w, pointsList)
    print(os.path.dirname(__file__))
    out_path = os.path.join(os.path.dirname(__file__), 'saved', 'track_v3_data.csv')
    xs_arr = np.asarray(xs, dtype=float)
    ys_arr = np.asarray(ys, dtype=float)
    csv_path = save_calibration_csv(out_path, None, xs_arr, ys_arr, header=None)
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'generate_stats.py'), '--screen-h', str(screen_h), '--screen-w', str(screen_w), '--input', str(out_path)])
    #   save_calibration_csv(out_path, None, xs_arr, ys_arr)
    #   my_map =  h_map.getAcopladeHist()
    """ heat_2 = make_heatmap(xs_arr, ys_arr, screen_h=screen_h, screen_w=screen_w, bins=80,
                                     smooth_sigma=1.2)
    heat_2["hist"].T
    #   axes = h_map.getAxis()

    #   print("Este es el het del EYEGESTURES: ",h_map)
    #   print("Axes _ Gestures", axes)
    out_path = os.path.join(os.path.dirname(__file__), "saved", "output")
    png_path = save_heatmap_png(heat_2 ,out_path)
    print(png_path)
    print("Tracking stopped.")
    stats = {"csv": csv_path, "samples": int(len(xs)), "total_time_s": float(total_time), "top_regions": top_regions, "png": png_path}
    save_report_pdf(out_path, png_path, stats)

    clb = gestures.clb[context_tag] """
    sys.exit(0)
# ...existing code...




""" 
(array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0., 464.]), 
    array([  0.,   0., 0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   1.,   4.,   1.,   3.,   3.,
         1.,   1.,   1.,   1.,   1.,   1.,   0.,   1.,   0.,   1.,   0.,
         1.,   1.,   0.,   1.,   0.,   0.,   2.,   0.,   0.,   1.,   1.,
         3.,  10.,   4.,  10.,   9.,  13.,  10.,  18.,  14.,  15.,  19.,
         6.,   4.,  12.,   3.,   9.,   5.,   4.,   4., 265.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.]))
        [[-463.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0], 
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -264.0, -3.0,
        -3.0, -4.0, -8.0, -2.0, -11.0, -3.0, -5.0, -18.0, -14.0, -13.0, -17.0, -9.0, -12.0, -8.0,
        -9.0, -3.0, -9.0, -2.0, 0.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
            1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -2.0, -2.0, 0.0, -3.0, 0.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                1.0, 1.0]]
"""