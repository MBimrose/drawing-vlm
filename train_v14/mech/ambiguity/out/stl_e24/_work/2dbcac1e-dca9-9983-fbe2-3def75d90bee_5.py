from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 15.0
rib_height = 3.0
hole_diameter = 6.5
hole_offset = 10.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 2.5
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body + rib

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

pocket = Pos(0, 0, plate_thickness/2 + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "plate_with_rib_holes_pocket"
export_step(part, "output.step")