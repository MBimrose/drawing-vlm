from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_height = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 10.0
hole_rows = 3
hole_cols = 4
chamfer_size = 1.0

solid_body = Box(outer_width, outer_depth, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(0, 0, -outer_height/2 + pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, outer_depth/2 - wall_thickness/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, wall_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_pocket_and_holes"
export_step(part, "output.step")