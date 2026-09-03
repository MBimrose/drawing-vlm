from build123d import *

block_width = 80.0
block_depth = 80.0
block_height = 30.0
bearing_diameter = 40.0
bearing_depth = 12.0
set_screw_diameter = 5.0
set_screw_offset = 10.0
chamfer_distance = 2.0

solid_body = Box(block_width, block_depth, block_height)

bearing_hole = Pos(0, 0, block_height/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_hole

set_screw_hole = Pos(block_width/2 - set_screw_offset, 0, 0) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, block_depth)
solid_body = solid_body - set_screw_hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "bearing_block"
export_step(part, "output.step")