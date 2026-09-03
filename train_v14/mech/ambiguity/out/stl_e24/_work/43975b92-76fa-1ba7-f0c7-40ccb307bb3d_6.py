from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 5.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 10.0
vent_hole_diameter = 4.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 15.0
vent_spacing_y = 10.0
chamfer_size = 1.0

solid = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

top_edges = solid.faces().sort_by(Axis.Z)[-1].edges()
solid = chamfer(top_edges, chamfer_size)

hole_r = vent_hole_diameter / 2
hole_h = outer_width + 20
for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        z = outer_height/2 + (j - (vent_rows - 1) / 2) * vent_spacing_y
        hole = Pos(x, outer_width/2, z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
        solid = solid - hole

part = solid
part.name = "vented_box"
export_step(part, "output.step")