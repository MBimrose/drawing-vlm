from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
central_hole_dia = 20.0
rib_width = 10.0
rib_height = 4.0
mount_hole_dia = 6.0
mount_hole_offset = 10.0
counterbore_radius = 3.0
counterbore_outer = 6.0
counterbore_depth = 2.0
slot_width = 4.0
slot_length = 20.0
chamfer_size = 1.0

result = Box(plate_length, plate_width, plate_thickness)
result = result - Cylinder(central_hole_dia/2, plate_thickness)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length - 2*rib_width, plate_width - 2*rib_width, rib_height)
result = result + rib

mount_points = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset)
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)
    result = result - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_outer, counterbore_depth)

slot_positions = [
    (0, plate_width/2 - slot_width/2),
    (0, -plate_width/2 + slot_width/2),
    (plate_length/2 - slot_width/2, 0),
    (-plate_length/2 + slot_width/2, 0)
]
for x, y in slot_positions:
    result = result - Pos(x, y, 0) * Box(slot_width, slot_length, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")