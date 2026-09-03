from build123d import *

plate_length = 90.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
slot_width = 10.0
slot_length = 20.0
rib_width = 12.0
rib_length = 30.0
rib_height = 4.0
chamfer_size = 0.8
pocket_depth = 2.0
pocket_margin = 4.0

result = Box(plate_length, plate_width, plate_thickness)

slot_x = plate_length / 2 - slot_length / 2
result = result - Pos(slot_x, 0, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - Pos(-slot_x, 0, 0) * Box(slot_length, slot_width, plate_thickness)

hole_x = plate_length / 2 - mount_hole_offset
hole_y = plate_width / 2 - mount_hole_offset
for x, y in [(hole_x, hole_y), (-hole_x, hole_y), (-hole_x, -hole_y), (hole_x, -hole_y)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness)

result = result + Pos(0, 0, plate_thickness / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

result = result - Pos(0, 0, plate_thickness / 2 + boss_height - pocket_depth / 2) * Cylinder(boss_diameter / 2, pocket_depth)

result = result - Pos(0, 0, plate_thickness / 2 + boss_height / 2) * Cylinder(mount_hole_diameter / 2, boss_height)

result = result + Pos(0, 0, -plate_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")