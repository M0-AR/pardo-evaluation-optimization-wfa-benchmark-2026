"""Tiny demo GIF: rolling WFA windows sweep SPY (fast-loading, README-friendly <2MB)."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter

spy = pd.read_csv("data_cache/SPY_2015-01-01_2026-10-10.csv", parse_dates=["Date"], index_col="Date")
close = spy["Close"]
fig, ax = plt.subplots(figsize=(8, 4))
frames = []
# 12 snapshots: growing IS (blue) + OOS (red) sweeping forward
n = len(close)
IS, OOS, STEP = 756, 126, 200
starts = list(range(0, n - IS - OOS, STEP))[:12]
ims = []
for s in starts:
    ax.clear()
    ax.plot(close.index, close, color="gray", linewidth=0.8, alpha=0.7)
    ax.axvspan(close.index[s], close.index[s + IS], color="blue", alpha=0.25, label="IS optimize")
    ax.axvspan(close.index[s + IS], close.index[s + IS + OOS], color="red", alpha=0.35, label="OOS test")
    ax.set_title(f"Walk-forward sweep {s // STEP + 1}/{len(starts)} — blue=optimize, red=locked test")
    ax.legend(fontsize=8)
    fig.canvas.draw()
    ims.append([ax])
print("rendering demo gif...")
# simpler: save sequential PNGs then assemble via PIL (no imagemagick needed)
import io
from PIL import Image
pil_frames = []
for s in starts:
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(close.index, close, color="gray", linewidth=0.8)
    ax2.axvspan(close.index[s], close.index[s + IS], color="blue", alpha=0.25)
    ax2.axvspan(close.index[s + IS], close.index[s + IS + OOS], color="red", alpha=0.4)
    ax2.set_title(f"Walk-forward {s // STEP + 1}/{len(starts)}: optimize BLUE, test RED (locked)")
    buf = io.BytesIO()
    fig2.savefig(buf, format="png", dpi=80)
    plt.close(fig2)
    buf.seek(0)
    pil_frames.append(Image.open(buf).convert("P"))
pil_frames[0].save("docs/demo.gif", save_all=True, append_images=pil_frames[1:], duration=700, loop=0)
print("wrote docs/demo.gif", len(pil_frames), "frames")
