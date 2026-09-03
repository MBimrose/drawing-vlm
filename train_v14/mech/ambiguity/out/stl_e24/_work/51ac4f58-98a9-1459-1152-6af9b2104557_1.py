from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 3.0
hole_diameter = 7.0
hole_spacing = 30.0
fillet_radius = 0.5
rib_height = 2.0
rib_width = 5.0

solid_body = Box(plate_length, plate_width, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")