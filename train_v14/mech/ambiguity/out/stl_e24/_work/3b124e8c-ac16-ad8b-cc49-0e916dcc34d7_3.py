from build123d import *

plate_width = 90.0
plate_depth = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
pocket_width = 20.0
pocket_depth = 12.0
pocket_height = 4.0
central_hole_diameter = 5.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
slot_length = 30.0
slot_width = 8.0
chamfer_size = 0.8

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

pocket = Pos(0, 0, plate_thickness + boss_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

result = result - Pos(0, 0, (plate_thickness + boss_height)/2) * Cylinder(central_hole_diameter/2, plate_thickness + boss_height + 0.1)

mount_points = [
    (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 0.1)

slot = Box(slot_length, slot_width, plate_thickness + 0.1)
result = result - Pos(-plate_width/2 + slot_width/2, 0, plate_thickness/2) * slot
result = result - Pos(plate_width/2 - slot_width/2, 0, plate_thickness/2) * slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")