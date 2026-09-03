from build123d import *

frame_length = 80.0
frame_width = 60.0
frame_height = 30.0
wall_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 10.0
hole_rows = 3
hole_cols = 4
chamfer_distance = 1.0

solid = Box(frame_length, frame_width, frame_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(0, 0, frame_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

top_edges = solid.faces().sort_by(Axis.Z)[-1].edges()
solid = chamfer(top_edges, chamfer_distance)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, frame_width/2 - wall_thickness/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, wall_thickness)
        solid = solid - hole

part = solid
part.name = "hollow_frame_with_pocket_and_holes"
export_step(part, "output.step")