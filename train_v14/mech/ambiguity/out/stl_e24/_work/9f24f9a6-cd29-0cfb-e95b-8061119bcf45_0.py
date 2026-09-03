from build123d import *

base_width = 80.0
base_depth = 20.0
base_thickness = 5.0
boss_diameter = 20.0
boss_height = 30.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_depth = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
notch_width = 5.0
notch_height = 10.0
chamfer_size = 0.5

base = Box(base_width, base_depth, base_thickness)
notch = Pos(base_width/2 - notch_width/2, 0, 0) * Box(notch_width, notch_height, base_thickness)
base = base - notch
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

boss = Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = result - Cylinder(set_screw_diameter/2, boss_height + base_thickness)
result = result - Pos(0, 0, boss_height/2 - set_screw_head_depth/2) * Cone(set_screw_diameter/2, set_screw_head_diameter/2, set_screw_head_depth)

for x in [-base_width/2 + mount_hole_offset, base_width/2 - mount_hole_offset]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, base_thickness + boss_height)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")