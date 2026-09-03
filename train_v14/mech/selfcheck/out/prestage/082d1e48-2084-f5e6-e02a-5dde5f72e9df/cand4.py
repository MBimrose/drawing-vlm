from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 24.0
fillet_radius = 2.0
hole_diameter = 8.0
hole_offset_from_end = 15.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(block_length/2 - hole_offset_from_end, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, block_length)
solid_body = solid_body - hole

part = solid_body
part.name = "filleted_block_with_pocket_and_hole"
export_step(part, "output.step")