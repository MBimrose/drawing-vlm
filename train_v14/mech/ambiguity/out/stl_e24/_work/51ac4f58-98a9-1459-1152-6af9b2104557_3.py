from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 3.0
hole_diameter = 7.0
hole_offset = 10.0
rib_thickness = 3.0
rib_height = 2.0
chamfer_distance = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-plate_length/2 + hole_offset, 0),
    (plate_length/2 - hole_offset, 0),
    (0, plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, plate_thickness/2 - pocket_depth + rib_height/2) * Box(rib_thickness, pocket_width, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")