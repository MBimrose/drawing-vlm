from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 10.0
opening_width = 40.0
opening_length = 40.0
hole_diameter = 5.0
hole_offset = 10.0
mid_hole_offset = 20.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_length, plate_thickness)
solid_body = solid_body - Box(opening_width, opening_length, plate_thickness)

hole_positions = [
    (plate_width/2 - hole_offset, plate_length/2 - hole_offset),
    (-plate_width/2 + hole_offset, plate_length/2 - hole_offset),
    (-plate_width/2 + hole_offset, -plate_length/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_length/2 + hole_offset),
    (0, plate_length/2 - mid_hole_offset),
    (0, -plate_length/2 + mid_hole_offset),
    (plate_width/2 - mid_hole_offset, 0),
    (-plate_width/2 + mid_hole_offset, 0),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_opening_and_holes"
export_step(part, "output.step")