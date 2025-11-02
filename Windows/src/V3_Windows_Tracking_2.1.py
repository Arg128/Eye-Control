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

import pygame

from eyeGestures import EyeGestures_v3
from eyeGestures.utils import VideoCapture
# archivo "check" que define ensure_face_present / open_video_source en tu repo
from check import ensure_face_present, open_video_source
from calib_io import load_calibration_npz, load_sklearn_model
from sklearn.linear_model import Ridge

# --- config ---
context_tag = "eye_Tracker_v3"

# screen size
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

# face check: run and wait (use sys.executable so the same Python is used)
face_check_path = os.path.join(os.path.dirname(__file__), "face_check.py")
try:
    cp = subprocess.run([sys.executable, face_check_path, "--show", "--frames", "40", "--threshold", "0.9"], check=False)
    if cp.returncode != 0:
        print("Face check returned non-zero. Continuing but warning: detection may be unstable.")
except Exception as e:
    print("Could not run face_check.py:", e)

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
            mouse.move(x, y, absolute=True, duration=0)
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

except KeyboardInterrupt:
    print("Tracking interrupted by user.")
finally:
    try:
        if hasattr(_cap, "release"):
            _cap.release()
        elif hasattr(cap, "release"):
            cap.release()
    except Exception:
        pass
    print("Tracking stopped.")
# ...existing code...