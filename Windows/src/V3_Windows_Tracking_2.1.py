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

from eyeGestures import EyeGestures_v3
from eyeGestures.utils import VideoCapture
# archivo "check" que define ensure_face_present / open_video_source en tu repo
from check import ensure_face_present, open_video_source

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

# model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), ".pkl", "calibration_model_v3.pkl")
if not os.path.exists(MODEL_PATH):
    print("No model found. Run run_calibration_v3_pygame.py first.")
    sys.exit(1)

# load gestures & model
gestures = EyeGestures_v3()
if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
    except Exception:
        pass
else:
    gestures.uploadCalibrationMap(np.array([[0.5, 0.5]]), context=context_tag)

print(f"Loading model from {MODEL_PATH}...")

with open(MODEL_PATH, "rb") as f:
    data = f.read()
gestures.loadModel(data, context=context_tag)

# camera: request a stable resolution similar to calibration (adjust if needed)
CAP_WIDTH = 1280
CAP_HEIGHT = 720
print(f"Opening camera with resolution {CAP_WIDTH}x{CAP_HEIGHT}...")
cap = open_video_source(0)
""" try:
    cap.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(CAP_WIDTH))
    cap.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(CAP_HEIGHT))
except Exception:
    pass """

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
_debug_frames = 6
iter = 0
print("Starting V3 tracking loop. Press (Ctrl) to stop.")
stop = False

# --- after initialization and flags (APPLY_ROT90, MIRROR_X, frame_time, etc.) ---

# Helper: get a usable cap object (wrapper vs raw cv2 capture)
_cap = cap
if not hasattr(_cap, "read") and hasattr(_cap, "cap"):
    _cap = _cap.cap

_debug_frames = 6
iter_count = 0

print("Starting V3 tracking loop. Press Ctrl to stop.")
try:
    while True:
        # stop via keyboard (non-blocking check)
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
            time.sleep(frame_time)
            continue

        # validate evt and point
        if evt is None or getattr(evt, "point", None) is None:
            # optionally debug
            # print("No event or point")
            time.sleep(frame_time)
            continue

        raw = np.asarray(evt.point, dtype=float).flatten()
        if raw.size < 2 or np.any(np.isnan(raw)) or np.any(np.isinf(raw)):
            print("Invalid evt.point:", raw)
            time.sleep(frame_time)
            continue

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

        # clip and cast to int
        x = int(np.clip(px, 0, screen_w - 1))
        y = int(np.clip(py, 0, screen_h - 1))

        # move mouse safely
        try:
            mouse.move(x, y, absolute=True, duration=0)
        except Exception as e:
            warnings.warn(f"mouse.move error: {e}")

        # optional debug print (limited)
        if iter_count < 10:
            print(f"raw={raw} -> px/py=({px:.1f},{py:.1f}) -> clipped=({x},{y})")

        # rate control
        time.sleep(frame_time)
        iter_count += 1

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