from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 3.0
central_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 2.0
chamfer_distance = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib_outer = Box(plate_length + 2 * rib_width, plate_width + 2 * rib_width, rib_height)
rib_inner = Box(plate_length, plate_width, rib_height)
rib = rib_outer - rib_inner
result = base + rib

result = result - Cylinder(central_hole_diameter / 2, plate_thickness + rib_height + 10)

mount_points = [
    (plate_length / 2 - mount_hole_offset, plate_width / 2 - mount_hole_offset),
    (-plate_length / 2 + mount_hole_offset, plate_width / 2 - mount_hole_offset),
    (-plate_length / 2 + mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    (plate_length / 2 - mount_hole_offset, -plate_width / 2 + mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness + rib_height + 10)

result = result - Pos(0, 0, plate_thickness - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)

result = chamfer(result.edges(), chamfer_distance)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")