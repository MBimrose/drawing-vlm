from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 8.0
central_hole_diameter = 20.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
counterbore_diameter = 12.0
counterbore_depth = 2.0
rib_width = 40.0
rib_height = 4.0
slot_width = 4.0
slot_length = 30.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_height/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_width, rib_height)
solid_body = solid_body + rib

slot_positions = [
    (0, -plate_height/2 + slot_width/2),
    (0,  plate_height/2 - slot_width/2),
    (-plate_width/2 + slot_width/2, 0),
    ( plate_width/2 - slot_width/2, 0),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_width, slot_length, plate_thickness)

part = solid_body
part.name = "plate_with_rib_and_slots"
export_step(part, "output.step")