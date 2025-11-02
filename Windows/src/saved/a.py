import zipfile
import os
# Descomprimir el archivo .npz
with zipfile.ZipFile("calib_v3_data.npz", 'r') as zip_ref:
    zip_ref.extractall(os.path.join(os.path.dirname(__file__), '..', 'saved'))
