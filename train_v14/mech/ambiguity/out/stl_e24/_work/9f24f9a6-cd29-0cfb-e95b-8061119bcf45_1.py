from build123d import *

base_width = 80.0
base_depth = 20.0
base_thickness = 6.0
boss_diameter = 20.0
boss_height = 30.0
slot_width = 5.0
slot_length = 15.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_depth = 2.5
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
chamfer_size = 0.5

base = Box(base_width, base_depth, base_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

slot = Pos(base_width / 2 - slot_width / 2, 0, 0) * Box(slot_width, slot_length, base_thickness)
result = result - slot

set_screw_hole = Pos(0, 0, boss_height / 2) * Cylinder(set_screw_diameter / 2, boss_height + 1)
result = result - set_screw_hole

csk_cone = Pos(0, 0, boss_height / 2 - set_screw_head_depth / 2) * Cone(set_screw_diameter / 2, set_screw_head_diameter / 2, set_screw_head_depth)
result = result - csk_cone

for x in [-mount_hole_spacing / 2, mount_hole_spacing]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, base_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")