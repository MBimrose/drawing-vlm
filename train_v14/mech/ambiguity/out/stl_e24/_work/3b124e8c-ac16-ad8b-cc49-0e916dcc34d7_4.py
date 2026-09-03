from build123d import *

plate_width = 90.0
plate_depth = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
recess_depth = 2.0
recess_margin = 4.0
central_hole_diameter = 5.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
slot_width = 10.0
slot_length = 30.0
chamfer_size = 0.8

result = Box(plate_width, plate_depth, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result - Pos(0, 0, plate_thickness/2 + boss_height - recess_depth/2) * Cylinder((boss_diameter - recess_margin)/2, recess_depth)
result = result - Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(central_hole_diameter/2, boss_height + 0.1)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 0.1)

slot_centers = [
    (-plate_width/2 + slot_width/2, 0),
    (plate_width/2 - slot_width/2, 0),
]
for x, y in slot_centers:
    result = result - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness + 0.1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")