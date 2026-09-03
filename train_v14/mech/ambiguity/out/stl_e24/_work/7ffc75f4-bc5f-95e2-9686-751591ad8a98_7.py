from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_width = 30.0
vent_height = 10.0
fillet_radius = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

vent_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_width, wall_thickness, vent_height)
solid_body = solid_body - vent_cut

part = solid_body
part.name = "hollow_box_with_vent"
export_step(part, "output.step")