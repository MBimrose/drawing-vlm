from build123d import *

overall_length = 80.0
overall_width = 50.0
overall_height = 30.0
wall_thickness = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 8.0

solid_body = Box(overall_width, overall_length, overall_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, overall_height/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, overall_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_pocket_and_holes"
export_step(part, "output.step")