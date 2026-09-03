from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 3.0
rib_width = 5.0
hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
slot_length = 30.0
slot_width = 5.0
slot_spacing = 20.0
chamfer_size = 0.5
boss_diameter = 20.0
boss_height = 2.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Box(plate_length + 2 * rib_width, plate_width + 2 * rib_width, rib_height) - Box(plate_length, plate_width, rib_height)
boss = Cylinder(boss_diameter / 2, boss_height)

result = base + rib + boss

result = result - Cylinder(hole_diameter / 2, 20)

mount_points = [
    (-plate_length / 2 + mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    (plate_length / 2 - mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    (-plate_length / 2 + mount_hole_offset, plate_width / 2 - mount_hole_offset),
    (plate_length / 2 - mount_hole_offset, plate_width / 2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, 20)

slot_points = [(-slot_spacing / 2, 0), (slot_spacing / 2, 0)]
for x, y in slot_points:
    result = result - Pos(x, y, 0) * Box(slot_length, slot_width, 20)

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "plate_with_rib_boss_holes_slots"
export_step(part, "output.step")