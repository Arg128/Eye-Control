import cv2
import pygame
from eyeGestures.utils import VideoCapture
# --- helper: open video source robustly and set resolution ---
def open_video_source(source):
    # source: int index or path/URL
    try:
        src = int(source)
    except Exception:
        src = source
    cap_local = VideoCapture(src)
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