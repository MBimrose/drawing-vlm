from build123d import *

block_length = 80.0
block_width = 80.0
block_height = 30.0
pocket_radius = 20.0
pocket_depth = 12.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0

solid_body = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

hole = Pos(mount_hole_offset, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_and_hole"
export_step(part, "output.step")