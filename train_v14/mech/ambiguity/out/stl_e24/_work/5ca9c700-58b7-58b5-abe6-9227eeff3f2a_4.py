from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 100.0
wall_thickness = 5.0
pocket_width = 30.0
pocket_height = 40.0
pocket_depth = 30.0
pocket_offset = 20.0
through_hole_dia = 8.0
chamfer_dist = 1.0

solid_body = Box(outer_width, outer_height, length)
pocket = Pos(outer_width/2 - pocket_depth/2, pocket_offset, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket
hole = Cylinder(through_hole_dia/2, length)
solid_body = solid_body - hole
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_dist)

part = solid_body
part.name = "box_with_pocket_and_hole"
export_step(part, "output.step")