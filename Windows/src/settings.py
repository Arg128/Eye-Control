import os
import pickle

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "saved", "config.bin")
class Settings():
    def __init__(self):
        #   Running options

        self.createCalibration = True
        self.check_face = True
        self.calibration_points = 70

        #   Visual customization settings
        self.enable_translation = True
        self.language = "es"
        self.background_color = "red"

    def save(self):
        tmp_path = STORAGE_PATH + ".tmp"
        data = pickle.dumps(self)
        data_bytes = bytes(data)

        # atomic write with flush+fsync
        with open(tmp_path, "wb") as f:
            f.write(data_bytes)
            f.flush()   #Writing buffering data to disk
            os.fsync(f.fileno())    #Ensure data its writing to disk
        os.replace(tmp_path, STORAGE_PATH)
        print("YA SE HA REALIZADO LA INSCRIPCIÓN EN: ", STORAGE_PATH)
        f.close()
        return True
    def load():
        if not os.path.isfile(STORAGE_PATH):
            return
        with open(STORAGE_PATH, 'rb') as file:
            data = file.read()
        config = pickle.loads(data)
        return config