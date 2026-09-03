from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
rib_length = 30.0
rib_width = 20.0
rib_height = 2.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
hole_diameter = 3.0
hole_offset = 5.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = base + rib - pocket

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_pocket_holes"
export_step(part, "output.step")