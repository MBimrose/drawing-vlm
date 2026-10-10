from build123d import *

# ---- dimensions from the target drawing (Image 1) ----
overall_length = 80.0
boss_dia = 46.7
boss_radius = boss_dia / 2.0
bar_width = 26.7
thickness = 16.9
central_bore_dia = 36.3
mount_hole_dia = 15.4
mount_hole_spacing = 58.2          # 69.1 - 10.9
fillet_radius = 2.7

# ---- solid body: rectangular bar + central boss, both full thickness ----
base = Box(overall_length, bar_width, thickness)
boss = Cylinder(boss_radius, thickness)
body = base + boss

# ---- fillet all edges (drawing: 20x R2.7) ----
body = fillet(body.edges(), fillet_radius)

# ---- central through bore ----
body = body - Cylinder(central_bore_dia / 2, thickness * 2)

# ---- two mounting holes on the bar centreline ----
for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    body = body - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2, thickness * 2)

part = body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")