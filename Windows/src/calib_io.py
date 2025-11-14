import os
import numpy as np
import csv
from joblib import dump, load

def save_calibration_npz(path, X, Yx, Yy, meta=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez_compressed(path, X=np.asarray(X), Yx=np.asarray(Yx), Yy=np.asarray(Yy), meta=meta or {})
    return path

def load_calibration_npz(path):
    data = np.load(path, allow_pickle=True)
    return data["X"], data["Yx"], data["Yy"], (data.get("meta", {}) if "meta" in data else {})

def save_calibration_csv(path, X, Yx, Yy, header=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        # write row = [x0,x1,..., yx, yy]
        zip_iter = None
        row = None
        if X is not None:
            zip_iter = zip(X, Yx, Yy)
            for xi, yxi, yyi in zip_iter:
                row = [float(yxi), float(yyi)]
                row.append(list(np.asarray(xi).ravel()))
                print(row)
                writer.writerow(row)
        else:
            zip_iter = zip(Yx, Yy)
            for yxi, yyi in zip_iter:
                row = [float(yxi), float(yyi)]
                writer.writerow(row)
    return path

def load_calibration_csv(path, n_features=None):
    X, Yx, Yy = [], [], []
    with open(path, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            vals = [float(v) for v in row]
            if n_features is None:
                # assume last two cols are Yx,Yy
                #   n_features = len(vals) - 2
                n_features = 2
            """
            X.append(vals[:n_features])
            Yx.append(vals[n_features])
            Yy.append(vals[n_features + 1]) """
            Yx.append(vals[0])
            Yy.append(vals[1])
            if (len(vals) == 3):
                X.append(vals[2])

    return np.array(X), np.array(Yx), np.array(Yy)

def save_sklearn_model(path, model):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dump(model, path)
    return path

def load_sklearn_model(path):
    return load(path)