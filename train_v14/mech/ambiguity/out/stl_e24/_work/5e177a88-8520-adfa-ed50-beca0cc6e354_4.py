from build123d import *

block_width = 80.0
block_depth = 80.0
block_height = 30.0
bearing_diameter = 40.0
bearing_depth = 12.0
cross_hole_diameter = 5.0
cross_hole_spacing = 20.0
chamfer_size = 2.0

solid_body = Box(block_width, block_depth, block_height)

# Bearing pocket cut from top face
bearing_cut = Pos(0, 0, block_height/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_cut

# Cross hole through >Y face
cross_hole = Pos(block_width/2 - cross_hole_spacing, 0, 0) * Rot(90, 0, 0) * Cylinder(cross_hole_diameter/2, block_depth + 10)
solid_body = solid_body - cross_hole

# Chamfer bottom edges
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "bearing_block"
export_step(part, "output.step")