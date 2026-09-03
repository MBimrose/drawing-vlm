from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
groove_width = 20.0
groove_depth = 5.0
groove_length = outer_length - 2 * wall_thickness
hole_diameter = 4.0
hole_spacing = 20.0
hole_count = 3
fillet_radius = 0.5
rib_thickness = 2.0
rib_height = 5.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, outer_height - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

for i in range(hole_count):
    x = (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(x, 0, outer_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, outer_width)
    solid_body = solid_body - hole

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "shelled_box_with_groove_holes_rib"
export_step(part, "output.step")