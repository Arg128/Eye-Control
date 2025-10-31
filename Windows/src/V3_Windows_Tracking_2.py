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

# ----------------- NEW: debug + auto affine calibration -----------------
import math

# Preproc flags MUST match calibration script
APPLY_ROT90 = True
MIRROR_X = False

# If true, the script will prompt the user to look at 3 screen points
AUTO_3POINT_CAL = True

def sample_mean_prediction(prompt_text, target_screen_coord, duration=1.6, max_samples=120):
    print(prompt_text, " -> look at", target_screen_coord)
    time.sleep(0.8)  # small pause before sampling
    samples = []
    t0 = time.time()
    while time.time() - t0 < duration and len(samples) < max_samples:
        ret, f = cap.read()
        if not ret or f is None:
            continue
        frm = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        if APPLY_ROT90:
            frm = np.rot90(frm)
        if MIRROR_X:
            frm = np.flip(frm, axis=1)
        evt, _ = gestures.step(frm, False, screen_w, screen_h, context=context_tag)
        if evt and getattr(evt, "point", None) is not None:
            samples.append(evt.point)
    if not samples:
        return None
    return np.mean(np.array(samples), axis=0)

def compute_affine(src_pts, dst_pts):
    # solve for 2x3 affine transform T: [x',y',1] = A [x,y,1] with A 2x3
    # builds linear system and solves least squares
    src = np.asarray(src_pts).reshape(-1,2)
    dst = np.asarray(dst_pts).reshape(-1,2)
    N = src.shape[0]
    if N < 3:
        return None
    M = np.zeros((2*N, 6))
    b = dst.reshape(2*N)
    for i in range(N):
        x, y = src[i]
        M[2*i  ] = [x, y, 1, 0, 0, 0]
        M[2*i+1] = [0, 0, 0, x, y, 1]
    # solve M * a = b
    a, *_ = np.linalg.lstsq(M, b, rcond=None)
    A = a.reshape(2,3)
    return A

def apply_affine(A, pt):
    v = np.array([pt[0], pt[1], 1.0])
    out = A.dot(v)
    return out[0], out[1]

affine_A = None
if AUTO_3POINT_CAL:
    try:
        # three screen targets (left, center, right)
        left_t   = np.array([int(screen_w*0.10), int(screen_h*0.50)])
        center_t = np.array([int(screen_w*0.50), int(screen_h*0.50)])
        right_t  = np.array([int(screen_w*0.90), int(screen_h*0.50)])
        print("Auto 3-point calibration: please follow instructions on screen/console.")
        p_left  = sample_mean_prediction("Look LEFT target", left_t, duration=1.8)
        p_center= sample_mean_prediction("Look CENTER target", center_t, duration=1.8)
        p_right = sample_mean_prediction("Look RIGHT target", right_t, duration=1.8)
        if p_left is not None and p_center is not None and p_right is not None:
            src = [p_left, p_center, p_right]
            dst = [left_t, center_t, right_t]
            affine_A = compute_affine(src, dst)
            if affine_A is not None:
                print("Affine matrix computed. Will apply transform to all predictions.")
                print(affine_A)
            else:
                print("Affine computation failed; will proceed without transform.")
        else:
            print("Not enough samples for 3-point calibration; proceeding without transform.")
    except Exception as e:
        print("Auto 3-point calibration error:", e)
        
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

# try to get device FPS; fallback to 30
cap_fps = cap.cap.get(cv2.CAP_PROP_FPS)
try:
    target_fps = int(cap_fps) if cap_fps and cap_fps > 0 else 30
except Exception:
    target_fps = 30
frame_time = 1.0 / max(1, target_fps)
print(f"Target FPS for tracking: {target_fps} (frame_time={frame_time:.3f}s)")

# preproc flags (must match what you used during calibration)
APPLY_ROT90 = True        # calibrate used np.rot90(frame_rgb)
MIRROR_X = False          # set True if data is mirrored
MAX_ITER = 1000
# safety: small debug prints for first frames
_debug_frames = 6
iter = 0
print("Starting V3 tracking loop. mouse middle click to stop.")
stop = False
def stop_tracking():
    global stop
    stop = True
mouse.on_middle_click(stop_tracking)

try:
    while not stop:
        mouse.on_right_click(lambda: print("Right Button clicked."))
        if iter > MAX_ITER:
            break
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            iter += 1
            continue

        # preprocess exactly as in calibration
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if APPLY_ROT90:
            frame_rgb = np.rot90(frame_rgb)
        # optional horizontal flip if needed
        if MIRROR_X:
            frame_rgb = np.flip(frame_rgb, axis=1)

        # call gestures.step once per frame
        try:
            evt, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        except Exception as ex:
            # don't crash tracking loop; print once then continue
            warnings.warn(f"gestures.step() error: {ex}")
            time.sleep(frame_time)
            continue

        if evt is not None and getattr(evt, "point", None) is not None:
            raw = np.array(evt.point, dtype=float)

            # optional mirror correction (if you observe left-right inverted results)
            if MIRROR_X:
                raw[0] = screen_w - raw[0]

            # clip to screen bounds to avoid extreme values
            x = int(np.clip(raw[0], 0, screen_w - 1))
            y = int(np.clip(raw[1], 0, screen_h - 1))

            # move mouse (duration 0 for immediate move)
            try:
                mouse.move(x, y, absolute=True, duration=0)
            except Exception:
                # fallback: ignore move errors
                pass

            if _debug_frames > 0:
                print(f"raw=({raw[0]:.1f},{raw[1]:.1f}) -> clipped=({x},{y})")
                _debug_frames -= 1

        # control loop rate using time.sleep (use Python time, not pygame clock)
        time.sleep(frame_time)
        inter = 0
except KeyboardInterrupt:
    print("Tracking interrupted by user.")
finally:
    try:
        # close/cleanup camera
        if hasattr(cap, "release"):
            cap.release()
        elif hasattr(cap, "close"):
            cap.close()
    except Exception:
        pass
    print("Tracking stopped.")
# ...existing code...