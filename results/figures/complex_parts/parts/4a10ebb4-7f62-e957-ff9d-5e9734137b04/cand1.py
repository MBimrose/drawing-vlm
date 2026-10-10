from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
chamfer_distance = 1.0
opening_width = 40.0
opening_height = 20.0
opening_offset_y = 5.0
hole_diameter = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
rib_thickness = 2.0
rib_height = 4.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

opening_cut = Pos(0, outer_width/2 - wall_thickness/2, opening_offset_y) * Box(opening_width, wall_thickness, opening_height)
solid_body = solid_body - opening_cut

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)

rib = Pos(0, 0, -rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "shelled_box_with_opening_holes_and_rib"
export_step(part, "output.step")