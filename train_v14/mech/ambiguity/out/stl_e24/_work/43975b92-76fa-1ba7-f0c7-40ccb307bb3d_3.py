from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 5.0
pocket_length = 50.0
pocket_width = 40.0
pocket_depth = 5.0
hole_diameter = 4.0
hole_rows = 3
hole_cols = 4
hole_spacing_x = 15.0
hole_spacing_y = 10.0
chamfer_size = 1.0

solid = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

top_edges = solid.faces().sort_by(Axis.Z)[-1].edges()
solid = chamfer(top_edges, chamfer_size)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = outer_height/2 + (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, outer_width/2 - wall_thickness/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, wall_thickness)
        solid = solid - hole

part = solid
part.name = "shelled_box_with_pocket_and_holes"
export_step(part, "output.step")