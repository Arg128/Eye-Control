import os
import sys
import cv2
import ctypes
import mouse
from eyeGestures import EyeGestures_v3
from eyeGestures.utils import VideoCapture
import numpy as np

context_tag = "eye_Tracker_v3"

# screen size
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

MODEL_PATH = os.path.join(os.path.dirname(__file__), ".pkl", "calibration_model_v3.pkl")
if not os.path.exists(MODEL_PATH):
    print("No model found. Run run_calibration_v3_pygame.py first.")
    sys.exit(1)

gestures = EyeGestures_v3()
# ensure context exists
if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
    except Exception:
        pass
else:
    # fallback minimal map
    gestures.uploadCalibrationMap(np.array([[0.5, 0.5]]), context=context_tag)

# load model bytes
with open(MODEL_PATH, "rb") as f:
    data = f.read()
gestures.loadModel(data, context=context_tag)

cap = VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        event, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        if event:
            x, y = int(event.point[0]), int(event.point[1])
            mouse.move(x, y, absolute=True, duration=0.01)
except KeyboardInterrupt:
    pass
finally:
    try:
        cap.release()
    except Exception:
        pass
    print("Tracking stopped.")