from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 40.0
wall_thickness = 2.0
corner_fillet_radius = 3.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3

solid_body = Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_fillet_radius)

y_center = outer_depth / 2
z_center = outer_height / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = z_center + (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y_center, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, outer_depth)
        solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_holes"
export_step(part, "output.step")