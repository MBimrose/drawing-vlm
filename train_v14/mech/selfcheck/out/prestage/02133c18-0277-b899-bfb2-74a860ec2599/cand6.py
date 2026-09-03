from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 3.0
hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
chamfer_size = 0.5

base = Box(plate_width, plate_height, plate_thickness)
rib_outer = Box(plate_width + 2 * rib_width, plate_height + 2 * rib_width, rib_height)
rib_inner = Box(plate_width, plate_height, rib_height)
rib = rib_outer - rib_inner
solid_body = base + rib

solid_body = solid_body - Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)

mount_points = [
    (-plate_width / 2 + mount_hole_offset, -plate_height / 2 + mount_hole_offset),
    ( plate_width / 2 - mount_hole_offset, -plate_height / 2 + mount_hole_offset),
    (-plate_width / 2 + mount_hole_offset,  plate_height / 2 - mount_hole_offset),
    ( plate_width / 2 - mount_hole_offset,  plate_height / 2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness + rib_height + 10)

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")