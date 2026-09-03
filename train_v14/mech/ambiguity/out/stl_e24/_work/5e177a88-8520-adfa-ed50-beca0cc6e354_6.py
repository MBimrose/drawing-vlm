from build123d import *

block_width = 80.0
block_length = 80.0
block_height = 30.0
bearing_diameter = 40.0
bearing_depth = 12.0
set_screw_diameter = 5.0
set_screw_offset = 30.0
chamfer_distance = 2.0

solid_body = Box(block_width, block_length, block_height)

bearing_cut = Pos(0, 0, block_height/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_cut

set_screw_cut = Pos(set_screw_offset, 0, 0) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, block_length)
solid_body = solid_body - set_screw_cut

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "bearing_block"
export_step(part, "output.step")