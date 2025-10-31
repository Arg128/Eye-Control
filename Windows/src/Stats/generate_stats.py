import os
import sys
import glob
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Config: paths (ajusta si necesitas)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RECORDINGS_DIR = os.path.join(PROJECT_ROOT, "recordings")    # busca CSVs aquí
OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)

def find_latest_csv(dirpath):
    files = sorted(glob.glob(os.path.join(dirpath, "*.csv")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def load_gaze_csv(path):
    # Intenta leer columnas comunes:
    data = np.genfromtxt(path, delimiter=",", dtype=float, skip_header=1, invalid_raise=False)
    if data.size == 0:
        return None
    # heurístico: buscar columnas con rango grande (x,y)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    # asumimos que columnas contienen timestamp, x, y en algún orden; tratamos de detectar
    colmins = np.nanmin(data, axis=0)
    colmaxs = np.nanmax(data, axis=0)
    ranges = colmaxs - colmins
    # asumimos que x/y son columnas con rango > 0 y dentro de pantallas (0..5000)
    candidates = [i for i, r in enumerate(ranges) if r > 1 and r < 20000]
    if len(candidates) >= 2:
        # tomar las dos con rango mayor como x,y (no perfecto pero funciona para logs típicos)
        idx = sorted(candidates, key=lambda i: ranges[i], reverse=True)[:2]
        xs = data[:, idx[0]]
        ys = data[:, idx[1]]
        # si los valores parecen fuera de pantalla (muy grandes) normalizamos si posible
        return {"x": xs, "y": ys, "raw": data}
    return None

def compute_time_in_app(timestamps):
    # timestamps en segundos o ms: intentar detectar
    if np.median(timestamps) > 1e6:
        # probablemente ms -> convertir a s
        timestamps = timestamps / 1000.0
    # tiempo total = last - first (simple)
    return float(np.nanmax(timestamps) - np.nanmin(timestamps))

def make_heatmap(xs, ys, xdim=1920, ydim=1080, bins=80):
    pts = np.vstack([xs, ys]).T
    heatmap, xedges, yedges = np.histogram2d(pts[:,0], pts[:,1], bins=bins, range=[[0, xdim], [0, ydim]])
    return heatmap.T, xedges, yedges

def top_regions(heatmap, xedges, yedges, top_k=5):
    flat = heatmap.flatten()
    idx = np.argsort(flat)[::-1][:top_k]
    regs = []
    nx, ny = heatmap.shape
    for i in idx:
        r = i // ny
        c = i % ny
        x0, x1 = xedges[c], xedges[c+1]
        y0, y1 = yedges[r], yedges[r+1]
        regs.append(((x0,x1),(y0,y1), int(flat[i])))
    return regs

def save_results_png_pdf(heatmap, xedges, yedges, xs, ys, out_dir):
    timestamp = int(time.time())
    png_path = os.path.join(out_dir, f"heatmap_{timestamp}.png")
    pdf_path = os.path.join(out_dir, f"report_{timestamp}.pdf")

    fig, ax = plt.subplots(figsize=(10,6))
    extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
    ax.imshow(heatmap, cmap="hot", origin="lower", extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
    ax.set_title("Gaze heatmap")
    ax.set_xlim(xedges[0], xedges[-1])
    ax.set_ylim(yedges[0], yedges[-1])
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # PDF with image + simple stats
    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(10,12))
        ax.axis("off")
        ax.text(0.5, 0.95, "EyeGestures - Reporte de uso", ha="center", va="top", fontsize=16)
        ax.text(0.02, 0.88, f"Total samples: {len(xs)}", fontsize=10)
        pdf.savefig(fig); plt.close(fig)

        # add heatmap page
        fig2, ax2 = plt.subplots(figsize=(10,6))
        ax2.imshow(heatmap, cmap="hot", origin="lower", extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        ax2.set_title("Heatmap")
        pdf.savefig(fig2); plt.close(fig2)

    return png_path, pdf_path

def main():
    csv = find_latest_csv(RECORDINGS_DIR)
    if not csv:
        print(json.dumps({"error":"no_csv_found"}))
        sys.exit(2)
    gaze = load_gaze_csv(csv)
    if gaze is None:
        print(json.dumps({"error":"cannot_parse_csv"}))
        sys.exit(2)

    xs = gaze["x"]
    ys = gaze["y"]
    # if timestamps exist in raw data first col, try to estimate time
    timestamps = None
    try:
        timestamps = gaze["raw"][:,0]
    except Exception:
        timestamps = np.arange(len(xs))

    total_time = compute_time_in_app(timestamps)
    # assume screen size standard; optionally read from metadata
    screen_w, screen_h = 1920, 1080
    heatmap, xedges, yedges = make_heatmap(xs, ys, xdim=screen_w, ydim=screen_h, bins=80)
    regions = top_regions(heatmap, xedges, yedges, top_k=5)

    png_path, pdf_path = save_results_png_pdf(heatmap, xedges, yedges, xs, ys, OUT_DIR)

    result = {
        "csv": csv,
        "samples": int(len(xs)),
        "total_time_s": float(total_time),
        "top_regions": regions,
        "png": png_path,
        "pdf": pdf_path
    }
    print(json.dumps(result))
    sys.exit(0)

if __name__ == "__main__":
    main()