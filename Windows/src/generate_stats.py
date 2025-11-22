import os
import sys
import glob
import json
import time
import datetime
import argparse
from time import gmtime, strftime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

try:
    from scipy.ndimage import gaussian_filter
except Exception:
    gaussian_filter = None
from . import RUNNING_PATH
# Config: paths (ajusta si necesitas)
PROJECT_ROOT = os.path.abspath(RUNNING_PATH)
RECORDINGS_DIR = os.path.join(PROJECT_ROOT, "saved")    # busca CSVs aquí
OUT_DIR = os.path.join(RECORDINGS_DIR, "output")
#   os.makedirs(OUT_DIR, exist_ok=True)

def find_latest_csv(dirpath):
    files = sorted(glob.glob(os.path.join(dirpath, "*.csv")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def load_gaze_csv(path):
    # try to read numeric CSV, skip header
    try:
        data = np.genfromtxt(path, delimiter=",", dtype=float, skip_header=1, invalid_raise=False)
    except Exception:
        data = None
    if data is None or data.size == 0:
        return None
    if data.ndim == 1:
        data = data.reshape(1, -1)
    # detect two best candidate columns for x,y by range
    mins = np.nanmin(data, axis=0)
    maxs = np.nanmax(data, axis=0)
    ranges = maxs - mins
    # choose two columns with largest ranges
    cand = np.argsort(ranges)[::-1]
    if len(cand) < 2:
        return None
    x_idx, y_idx = cand[0], cand[1]
    xs = data[:, x_idx]
    ys = data[:, y_idx]
    return {"x": xs, "y": ys, "raw": data, "cols": (x_idx, y_idx)}

def compute_time_seconds(arr):
    # guess timestamps column if present (first column)
    try:
        t = np.asarray(arr).astype(float)
        if np.median(t) > 1e6:  # ms
            t = t / 1000.0
        return float(np.nanmax(t) - np.nanmin(t))
    except Exception:
        return 0.0

def make_heatmap(xs, ys, screen_w, screen_h, bins=80, smooth_sigma=None, custom_mode=False):
    # clip points to screen extents first
    xs_cl = np.clip(xs, 0, screen_w)
    ys_cl = np.clip(ys, 0, screen_h)
    H, xedges, yedges = np.histogram2d(xs_cl, ys_cl, bins=bins, range=[[0, screen_w], [0, screen_h]])
    # H shape is (xbins, ybins) -- transpose for image origin lower
    H = H.T  # now shape (ybins, xbins)
    if smooth_sigma and gaussian_filter is not None:
        H = gaussian_filter(H, sigma=smooth_sigma)
    return {"hist" : H, "xedges": xedges, "yedges" : yedges}

def make_heat_v2(heat_obj, point_list):
    hist = heat_obj.getHist()
    hist_x = hist[0]
    hist_y = hist[1]

    axis = heat_obj.getAxis()

    fig, ax = plt.subplots(figsize=(10,6))
    fig, bx = plt.subplots(figsize=(10,6))
    extent = [axis[0][0], axis[0][-1], axis[1][0], axis[1][-1]]

    ax.set_xlabel("X")
    bx.set_ylabel("Y")

    ax.set_title("Histogram to X")
    bx.set_title("Histogram to Y")
    
    return 

def top_regions_from_heatmap(heat, top_k=5):
    flat = heat["hist"].flatten()
    idx = np.argsort(flat)[::-1][:top_k]
    regs = []
    ny, nx = heat["hist"].shape
    for i in idx:
        r = i // nx
        c = i % nx
        x0, x1 = heat["xedges"][c], heat["xedges"][c+1]
        y0, y1 = heat["yedges"][r], heat["yedges"][r+1]
        regs.append({"box": [float(x0), float(x1), float(y0), float(y1)], "count": int(flat[i])})
    return regs

def save_heatmap_png(heat, out_path, cmap="hot"):
    fig, ax = plt.subplots(figsize=(10,6))
    timing = strftime("%a, %d %b %Y %H-%M-%S", gmtime())
    extent = [heat["xedges"][0], heat["xedges"][-1], heat["yedges"][0], heat["yedges"][-1]]
    ax.imshow(heat["hist"], cmap=cmap, origin="lower", extent=extent, aspect='auto')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Gaze heatmap")
    out_path = os.path.join(out_path, fr"HEATMAP IMAGE {timing}.png")
    """
    out_path = str(out_path).replace(':', '-')
    out_path = fr'{out_path}' """
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path

def save_report_pdf(pdf_path, png_path, stats):
    timing = strftime("%a, %d %b %Y %H-%M-%S", gmtime())
    pdf_path = os.path.join(pdf_path, f"Report {timing}.pdf")
    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(11,8.5))
        ax.axis("off")
        ax.text(0.5, 0.95, "EyeGestures - Reporte de uso", ha="center", va="top", fontsize=16)
        ax.text(0.02, 0.88, f"CSV: {stats.get('csv','-')}", fontsize=10)
        ax.text(0.02, 0.84, f"Samples: {stats.get('samples',0)}", fontsize=10)
        ax.text(0.02, 0.80, f"Total time (s): {stats.get('total_time_s',0):.2f}", fontsize=10)
        top = stats.get("top_regions", [])
        for i, r in enumerate(top):
            ax.text(0.02, 0.76 - i*0.04, f"Top {i+1}: box={r['box']} count={r['count']}", fontsize=9)
        pdf.savefig(fig); plt.close(fig)
        # heatmap page
        img = plt.imread(png_path)
        fig2, ax2 = plt.subplots(figsize=(11,8.5))
        ax2.imshow(img)
        ax2.axis("off")
        pdf.savefig(fig2); plt.close(fig2)
    return pdf_path

def main():
    p = argparse.ArgumentParser(description="Generate gaze heatmap + report")
    p.add_argument("--input", default=RECORDINGS_DIR, help="CSV file or directory (default: recordings/ in project root)")
    p.add_argument("--out", default=OUT_DIR, help="output folder (default: Stats/output in this module)")
    p.add_argument("--bins", type=int, default=80)
    p.add_argument("--smooth", type=float, default=1.2, help="gaussian sigma (0 disables smoothing)")
    p.add_argument("--screen-w", type=int, default=1920)
    p.add_argument("--screen-h", type=int, default=1080)
    p.add_argument("--top-k", type=int, default=5)
    args = p.parse_args()

    inp = args.input
    outdir = args.out
    os.makedirs(outdir, exist_ok=True)

    csv_file = inp if os.path.isfile(inp) else find_latest_csv(inp)
    if csv_file is None:
        print(json.dumps({"error": "no_csv_found", "searched": inp}))
        sys.exit(2)

    gaze = load_gaze_csv(csv_file)
    if gaze is None:
        print(json.dumps({"error": "cannot_parse_csv", "csv": csv_file}))
        sys.exit(2)

    xs = gaze["x"]
    ys = gaze["y"]
    raw = gaze.get("raw", None)
    total_time = 0.0
    if raw is not None:
        try:
            total_time = compute_time_seconds(raw[:,0])
        except Exception:
            total_time = 0.0

    heat_dict = make_heatmap(xs, ys, args.screen_w, args.screen_h, bins=args.bins,
                                     smooth_sigma=(args.smooth if args.smooth and args.smooth>0 else None))

    print(args.top_k)
    top_regions = top_regions_from_heatmap(heat_dict, top_k=args.top_k)
    png_path = save_heatmap_png(heat_dict, outdir)
    stats = {"csv": csv_file, "samples": int(len(xs)), "total_time_s": float(total_time), "top_regions": top_regions, "png": png_path}
    save_report_pdf(outdir, png_path, stats)

    print(json.dumps(stats))
    sys.exit(0)

if __name__ == "__main__":
    main()