from build123d import *

outer_length = 80.0
outer_width = 30.0
outer_height = 40.0
wall_thickness = 2.0
pocket_width = 30.0
pocket_depth = 6.0
pocket_height = 10.0
pocket_offset = 20.0
chamfer_size = 0.5
hole_diameter = 6.0
hole_offset = 15.0

solid = Box(outer_length, outer_width, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

pocket1 = Pos(-pocket_offset/2, 0, outer_height/2 - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid = solid - pocket1

pocket2 = Pos(pocket_offset/2, 0, outer_height/2 - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid = solid - pocket2

hole = Pos(outer_length/2, 0, hole_offset) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_length)
solid = solid - hole

right_face = solid.faces().sort_by(Axis.X)[-1]
right_edges = right_face.edges()
solid = chamfer(right_edges, chamfer_size)

part = solid
part.name = "shelled_box_with_pockets"
export_step(part, "output.step")