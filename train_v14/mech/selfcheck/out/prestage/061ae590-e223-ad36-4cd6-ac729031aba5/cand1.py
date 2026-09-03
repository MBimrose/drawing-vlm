from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
chamfer_size = 1.5
recess_radius = 15.0
recess_depth = 4.0
hole_radius = 8.0
hole_offset = 10.0
rib_width = 6.0
rib_thickness = 3.0
rib_height = 12.0
rib_offset_x = 20.0
rib_offset_y = 15.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body - Pos(0, 0, plate_thickness - recess_depth/2) * Cylinder(recess_radius, recess_depth)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_radius, plate_thickness)

rib_positions = [
    (-rib_offset_x, -rib_offset_y),
    ( rib_offset_x, -rib_offset_y),
    (-rib_offset_x,  rib_offset_y),
    ( rib_offset_x,  rib_offset_y)
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, plate_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

part = solid_body
part.name = "plate_with_recess_holes_and_ribs"
export_step(part, "output.step")