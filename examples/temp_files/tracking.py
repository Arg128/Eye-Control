import eyeGestures

# Initialize the eye-tracking system
tracker = eyeGestures.Tracker()

# Start tracking
tracker.start()

# Process gaze data
while True:
    gaze_data = tracker.get_gaze()
    print(f"Gaze coordinates: {gaze_data}")

# Stop tracking when done
tracker.stop()