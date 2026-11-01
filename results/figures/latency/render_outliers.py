import sys; sys.path.insert(0, "train_v14/geom")
from cad_render import render_stl
GT = "step_to_drw/wds_dataset/gt_meshes_v15"
for k in sys.argv[1:]:
    im = render_stl(f"{GT}/{k}.stl", color="#8a8f99", size=500); im.crop(im.getbbox()).save(f"results/figures/latency/outlier_renders/{k[:8]}.png"); print(k[:8])
