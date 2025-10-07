import os
import sys
import cv2
import numpy as np
import time
import mouse
import pygame

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures import EyeGestures_v2


def main():
    """     pygame.init()
    pygame.font.init()
    """
    gestures = EyeGestures_v2(calibration_radius=1000)
    cap = cv2.VideoCapture(0)

    # Build calibration map (normalizado 0..1)
    x = np.arange(0, 1.1, 0.2)
    y = np.arange(0, 1.1, 0.2)
    xx, yy = np.meshgrid(x, y)
    calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
    np.random.shuffle(calibration_map)
    gestures.uploadCalibrationMap(calibration_map, context="v2calib")
    gestures.setFixation(1.0)

    width = 1280
    height = 720

    n_points = min(len(calibration_map), 50)
    iterator = 0
    prev_pt = (-1, -1)

    print("Starting calibration (press 'q' to quit).")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            calibrate = (iterator <= n_points)
            event, cevent = gestures.step(frame, calibrate, width, height, context="v2calib")

            if cevent is not None:
                pt = tuple(map(int, cevent.point))
                print(f"Calib point: {pt}, acceptance_radius: {cevent.acceptance_radius}")
                if calibrate:
                    if pt != prev_pt:
                        iterator += 1
                        prev_pt = pt
                        print(f"Progress: {iterator}/{n_points}")

            # simple escape
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        model_bytes = gestures.saveModel(context="v2calib")
        if model_bytes:
            with open("calibration_model_v2.pkl", "wb") as f:
                f.write(model_bytes)
            print("Saved model to calibration_model_v2.pkl")
        else:
            print("No model to save.")
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
