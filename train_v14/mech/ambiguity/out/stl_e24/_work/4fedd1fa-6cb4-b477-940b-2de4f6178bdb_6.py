from build123d import *

plate_width = 60.0
plate_height = 60.0
plate_thickness = 8.0
slot_length = 30.0
slot_width = 10.0
central_hole_diameter = 12.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_thickness = 4.0
rib_width = 6.0
chamfer_distance = 2.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

solid_body = solid_body - Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness)

mount_points = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness)

rib = Box(rib_width, rib_width, rib_thickness)
solid_body = solid_body + Pos(plate_width / 2 + rib_width / 2, 0, 0) * rib
solid_body = solid_body + Pos(-plate_width / 2 - rib_width / 2, 0, 0) * rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")