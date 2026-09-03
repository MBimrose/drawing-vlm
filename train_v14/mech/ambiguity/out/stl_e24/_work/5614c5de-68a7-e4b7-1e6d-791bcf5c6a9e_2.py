from build123d import *

outer_width = 80.0
outer_depth = 50.0
outer_height = 20.0
wall_thickness = 3.0
corner_fillet_radius = 5.0
notch_width = 10.0
notch_depth = 6.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3

solid_body = Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_fillet_radius)
notch = Box(notch_width, notch_depth, outer_height)
solid_body = solid_body - Pos(outer_width/2 - wall_thickness/2, 0, 0) * notch
solid_body = solid_body - Pos(-outer_width/2 + wall_thickness/2, 0, 0) * notch
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, outer_height)

part = solid_body
part.name = "shelled_box_with_notches_and_holes"
export_step(part, "output.step")