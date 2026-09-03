from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
hole_diameter = 3.0
hole_offset = 5.0
rib_height = 2.0
rib_width = 5.0
rib_spacing = 12.0
chamfer_size = 0.4

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

num_ribs = int((plate_length - 2*hole_offset) // rib_spacing) + 1
for i in range(num_ribs):
    x = -plate_length/2 + hole_offset + i * rib_spacing
    rib = Pos(x, 0, rib_height/2) * Box(rib_width, plate_width - 2*hole_offset, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")