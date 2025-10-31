import argparse
import ctypes
import sys
import time
import json
import cv2
import numpy as np

user32 = ctypes.windll.user32
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)

# prefer wrapper if available, otherwise provide a factory function

def parse_args():
    p = argparse.ArgumentParser(description="Face check before calibration")
    p.add_argument("--source", default="0", help="camera index or path")
    p.add_argument("--frames", type=int, default=40, help="frames to sample")
    p.add_argument("--threshold", type=float, default=0.8, help="min fraction of frames with face")
    p.add_argument("--min-area-ratio", type=float, default=0.28,
                   help="min face area ratio (face_area / frame_area) to count as valid")
    p.add_argument("--width", type=int, default=WIDTH/3, help="force capture width")
    p.add_argument("--height", type=int, default=HEIGHT/4, help="force capture height")
    p.add_argument("--show", action="store_true", help="show preview window")
    return p.parse_args()

def open_cap(source, width=None, height=None):
    cap = cv2.VideoCapture(int(source))
    # if wrapper supports .set, attempt to fix resolution
    try:
        if width:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        if height:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
    except Exception:
        pass
    return cap


def main():
    args = parse_args()
    cap = open_cap(args.source, args.width, args.height)

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    detections = 0
    total = 0
    #   start = time.time()
    #   last_frame = None

    # Warm-up a few frames
    warm = 5
    print("Iniciando")
    for _ in range(warm):
        print("Seguimos")
        ret, f = cap.read()
        if not ret or f is None:
            print("Warning: unable to read from camera during warm-up")
            time.sleep(1)
            continue

    vis = None
    ok_flag = True
    while (True):
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("Warning: unable to read from camera")
            continue
        #   last_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

        total += 1
        valid = False
        area_ratio = 0.0
        if len(faces) > 0:
            # take largest face
            x,y,w,h = max(faces, key=lambda r: r[2]*r[3])
            frame_area = frame.shape[0] * frame.shape[1]
            face_area = w * h
            area_ratio = face_area / float(frame_area)
            if area_ratio >= args.min_area_ratio:
                detections += 1
                valid = True
            else:
                print("Por favor acérquese más a la cámara")

        frac = detections / float(total) if total > 0 else 0.0

        if args.show:
            vis = frame.copy()
            if len(faces) > 0:
                x,y,w,h = max(faces, key=lambda r: r[2]*r[3])
                color = (0,255,0) if valid else (0,165,255)
                cv2.rectangle(vis, (x,y), (x+w, y+h), color, 2)
                cv2.putText(vis, f"ratio:{area_ratio:.3f}", (x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            if area_ratio >= args.min_area_ratio:
                cv2.putText(vis, f"Detected: {detections}/{total} ({frac:.2f})", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            else:
                cv2.putText(vis, f"Please Stand up to Camera", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            cv2.imshow("Face check", vis)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # early exit if threshold satisfied (and at least a few frames sampled)
        if detections >= args.frames:
            break

        if cv2.getWindowProperty('Face check', cv2.WND_PROP_VISIBLE) < 1:
            break

    # final results
    cv2.destroyAllWindows()
    ok = detections >= args.frames
    result = {"ok": ok, "detections": int(detections), "frames": int(total), "fraction": float(detections/total) if total>0 else 0.0}
    print(json.dumps(result))
    time.sleep(3.5)
    # cleanup
    try:
        cap.release()
    except Exception:
        pass
    if args.show:
        cv2.destroyAllWindows()

    # exit code 0 = ok, 2 = not ok, 1 = error
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    print("Starting face check...")
    main()