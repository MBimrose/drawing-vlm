from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
fillet_radius = 1.0
snap_tab_width = 12.0
snap_tab_height = 6.0
snap_tab_thickness = 1.0
opening_width = 30.0
opening_height = 6.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)
tab = Pos(outer_length/2 + snap_tab_thickness/2, 0, outer_height/2) * Box(snap_tab_thickness, snap_tab_width, snap_tab_height)
solid_body = solid_body + tab
opening = Pos(-outer_length/2 + wall_thickness/2, 0, outer_height/2) * Box(wall_thickness, opening_width, opening_height)
solid_body = solid_body - opening
part = solid_body
part.name = "hollow_box_with_tab_and_opening"
export_step(part, "output.step")