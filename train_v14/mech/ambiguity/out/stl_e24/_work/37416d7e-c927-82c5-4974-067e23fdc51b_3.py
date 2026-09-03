from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
boss_radius = 8.0
boss_height = 5.0
chamfer_dist = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
pocket_depth = 2.0
pocket_margin = 2.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
boss = Pos(0, 0, arm_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_dist)

hole_positions = [
    (-arm_length/2 + mount_hole_offset, -arm_width/2 + mount_hole_dia/2 + 2),
    (-arm_length/2 + mount_hole_offset,  arm_width/2 - mount_hole_dia/2 - 2),
    ( arm_length/2 - mount_hole_offset, -arm_width/2 + mount_hole_dia/2 + 2),
    ( arm_length/2 - mount_hole_offset,  arm_width/2 - mount_hole_dia/2 - 2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, (arm_thickness + boss_height)/2) * Cylinder(mount_hole_dia/2, arm_thickness + boss_height + 2)

pocket_w = boss_radius * 2 - pocket_margin
pocket_h = boss_radius * 2 - pocket_margin
pocket = Pos(0, 0, arm_thickness + boss_height - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
result = result - pocket

part = result
part.name = "arm_with_boss"
export_step(part, "output.step")