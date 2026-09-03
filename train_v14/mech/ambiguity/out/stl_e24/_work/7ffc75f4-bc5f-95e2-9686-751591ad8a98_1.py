from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
inner_fillet_radius = 1.0
access_width = 30.0
access_height = 10.0
access_depth = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, inner_fillet_radius)

access_cut = Pos(0, outer_width/2 - access_depth/2, outer_height/2) * Box(access_width, access_depth, access_height)
solid_body = solid_body - access_cut

pocket_cut = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket_cut

part = solid_body
part.name = "shelled_box_with_access_and_pocket"
export_step(part, "output.step")