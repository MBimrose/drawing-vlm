from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 10.0
pocket_width = 20.0
pocket_length = 24.0
pocket_depth = 2.0
hole_diameter = 3.3
hole_spacing_x = 40.0
hole_spacing_y = 24.0
fillet_radius = 2.0
chamfer_distance = 0.5
rib_height = 4.0
rib_thickness = 2.0
rib_offset = 5.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

pocket = Pos(0, 0, bracket_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

rib = Pos(0, bracket_width/2 - rib_offset - rib_thickness/2, rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket"
export_step(part, "output.step")