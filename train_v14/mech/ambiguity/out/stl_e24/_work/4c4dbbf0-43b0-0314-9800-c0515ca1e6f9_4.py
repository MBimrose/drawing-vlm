from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 80.0
wall_thickness = 4.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 10.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_rows = 2
hole_cols = 3

solid_body = Box(outer_width, outer_height, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, -length/2 + pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        y = (i - (hole_cols-1)/2) * hole_spacing
        z = (j - (hole_rows-1)/2) * hole_spacing
        hole = Pos(outer_width/2, y, z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_width)
        solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_pocket_and_holes"
export_step(part, "output.step")