from build123d import *

plate_length = 80.0
plate_width = 20.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 30.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_depth = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
slot_width = 5.0
slot_length = 15.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
result = base + boss

csk_cone = Pos(0, 0, plate_thickness + boss_height - set_screw_head_depth) * Cone(set_screw_diameter / 2, set_screw_head_diameter / 2, set_screw_head_depth)
csk_cyl = Cylinder(set_screw_diameter / 2, plate_thickness + boss_height + 10)
result = result - csk_cone - csk_cyl

for x in [-plate_length / 2 + mount_hole_offset, plate_length / 2 - mount_hole_offset]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness + 10)

slot = Pos(plate_length / 2 - slot_width / 2, 0, 0) * Box(slot_width, slot_length, plate_thickness)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_mounts"
export_step(part, "output.step")