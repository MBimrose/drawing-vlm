from build123d import *

bracket_width = 60.0
bracket_depth = 40.0
bracket_height = 8.0
wall_thickness = 2.0
notch_width = 12.0
notch_depth = 4.0
hole_diameter = 5.0
hole_spacing = 30.0
fillet_radius = 0.2

solid_body = Box(bracket_width, bracket_depth, bracket_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch_box = Pos(bracket_width/2 - notch_depth/2, 0, 0) * Box(notch_depth, notch_width, bracket_height)
solid_body = solid_body - notch_box

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")