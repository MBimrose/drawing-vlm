from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 3.0
hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
chamfer_size = 0.5

base_plate = Box(plate_length, plate_width, plate_thickness)
rib = Box(plate_length + 2 * rib_width, plate_width + 2 * rib_width, rib_height) - Box(plate_length, plate_width, rib_height)
result = base_plate + rib

result = result - Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)

mount_points = [
    (-plate_length / 2 + mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    (plate_length / 2 - mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    (-plate_length / 2 + mount_hole_offset, plate_width / 2 - mount_hole_offset),
    (plate_length / 2 - mount_hole_offset, plate_width / 2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness + rib_height + 10)

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")