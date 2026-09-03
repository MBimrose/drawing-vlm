from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 4.0
fillet_radius = 2.0
pocket_margin = 6.0
pocket_depth = 8.0
hole_diameter = 5.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
pocket_length = inner_length - 2 * pocket_margin
pocket_width = inner_width - 2 * pocket_margin

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_width, outer_length, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, outer_height - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, outer_height / 2) * Cylinder(hole_diameter / 2, outer_height)
        solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_pocket_and_holes"
export_step(part, "output.step")