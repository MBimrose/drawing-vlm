from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 40.0
wall_thickness = 2.0
corner_fillet = 3.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 3
hole_spacing_x = 20.0
hole_spacing_y = 15.0

solid_body = Box(outer_width, outer_depth, outer_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, outer_depth / 2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, outer_depth)

part = solid_body
part.name = "shelled_box_with_holes"
export_step(part, "output.step")