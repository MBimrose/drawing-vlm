import json, glob, numpy as np, matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager as fm
for f in glob.glob("fonts/*.ttf"): fm.fontManager.addfont(f)
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import trimesh
plt.rcParams["font.family"] = "Liberation Sans"; plt.rcParams["svg.fonttype"] = "none"
S = "cm_02b4260a"; d = json.load(open(f"{S}/data.json"))
M = np.array(d["pair_iou"], dtype=float); gt = np.array(d["iou"], dtype=float); ex = d["exec"]; n = len(gt)
labels = [f"c{j}" for j in range(n)]
fig = plt.figure(figsize=(8, 10.2))
gs = fig.add_gridspec(2, 1, height_ratios=[1.6, 7.0], hspace=0.0)
# --- thumbnails of the 8 candidate solids (same camera), aligned with the heatmap columns
top = gs[0].subgridspec(1, n, wspace=0.05)
def show_mesh(ax, path):
    m = trimesh.load(path, force="mesh")
    v = m.vertices - m.bounds.mean(axis=0); s = (m.bounds[1] - m.bounds[0]).max() / 2
    v = v / s; f = m.faces
    ax.plot_trisurf(v[:, 0], v[:, 1], v[:, 2], triangles=f, color="#3b6fc4", edgecolor="black", linewidth=0.08, alpha=0.95, shade=True)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1); ax.view_init(elev=28, azim=-50); ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()
for j in range(n):
    ax = fig.add_subplot(top[0, j], projection="3d")
    p = f"{S}/stl/cand{j}.stl"
    try: show_mesh(ax, p)
    except Exception: ax.text2D(0.5, 0.5, "no solid", ha="center", va="center", fontsize=9, fontweight="bold", transform=ax.transAxes); ax.set_axis_off()
    ax.set_title(f"c{j}", fontsize=11, fontweight="bold", pad=-2)
# --- heatmap: pairwise IoU off-diagonal (Blues), ground-truth IoU on the diagonal (grey ramp), values annotated
ax = fig.add_subplot(gs[1])
A = M.copy(); A[np.isnan(A)] = 0.0
off = np.ma.masked_where(np.eye(n, dtype=bool), A)
ax.imshow(off, cmap="Blues", vmin=0.0, vmax=1.0, aspect="equal")
diag = np.ma.masked_where(~np.eye(n, dtype=bool), np.tile(gt, (n, 1)) * np.eye(n))
ax.imshow(diag, cmap="Greys", vmin=0.55, vmax=1.15, aspect="equal")
for i in range(n):
    for j in range(n):
        if i == j:
            txt = f"GT\n{gt[i]:.2f}" if ex[i] else "GT\nfail"; col = "white" if gt[i] >= 0.9 else "black"
        elif np.isnan(M[i, j]):
            txt = "–"; col = "#888888"
        else:
            txt = f"{M[i, j]:.2f}"; col = "white" if M[i, j] > 0.6 else "black"
        ax.text(j, i, txt, ha="center", va="center", fontsize=10, fontweight="bold", color=col)
ax.set_xticks(range(n)); ax.set_yticks(range(n)); ax.set_xticklabels(labels, fontsize=11, fontweight="bold"); ax.set_yticklabels(labels, fontsize=11, fontweight="bold")
ax.set_xticks(np.arange(-0.5, n, 1), minor=True); ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
ax.grid(which="minor", color="black", linewidth=0.5); ax.tick_params(which="minor", bottom=False, left=False)
ax.tick_params(which="major", top=True, right=True, direction="in", length=0)
ax.set_xlabel("Candidate", fontsize=13, fontweight="bold", labelpad=10); ax.set_ylabel("Candidate", fontsize=13, fontweight="bold", labelpad=10)
mean_agree = np.nanmean(np.where(np.eye(n, dtype=bool), np.nan, M), axis=1)
ax2 = ax.secondary_yaxis("right"); ax2.set_yticks(range(n)); ax2.set_yticklabels([f"agree {a:.2f}" if not np.isnan(a) else "–" for a in mean_agree], fontsize=10, fontweight="bold"); ax2.tick_params(length=0)
fig.savefig(f"{S}/pairwise_iou_02b4260a.svg", format="svg", dpi=300, bbox_inches="tight")
fig.savefig(f"{S}/pairwise_iou_02b4260a.png", format="png", dpi=300, bbox_inches="tight")
s = open(f"{S}/pairwise_iou_02b4260a.svg").read().replace("Liberation Sans", "Arial"); open(f"{S}/pairwise_iou_02b4260a.svg", "w").write(s)
print("mean agreement:", np.round(mean_agree, 3), "medoid:", int(np.nanargmax(mean_agree)), "oracle:", int(np.argmax(gt)))
