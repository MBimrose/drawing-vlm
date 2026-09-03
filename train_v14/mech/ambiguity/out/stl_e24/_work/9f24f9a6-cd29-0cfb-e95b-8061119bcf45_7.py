from build123d import *

base_length = 80.0
base_width = 20.0
base_thickness = 5.0
boss_diameter = 20.0
boss_height = 30.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_depth = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
slot_width = 5.0
slot_length = 30.0
slot_depth = 3.0
chamfer_size = 0.5

base = Box(base_length, base_width, base_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

csk_cone = Pos(0, 0, boss_height/2 - set_screw_head_depth/2) * Cone(set_screw_diameter/2, set_screw_head_diameter/2, set_screw_head_depth)
csk_cyl = Pos(0, 0, 0) * Cylinder(set_screw_diameter/2, boss_height + 10)
result = result - (csk_cone + csk_cyl)

mount_hole = Pos(-base_length/2 + mount_hole_offset, 0, 0) * Cylinder(mount_hole_diameter/2, base_thickness + 10)
result = result - mount_hole

slot = Pos(base_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_length)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")