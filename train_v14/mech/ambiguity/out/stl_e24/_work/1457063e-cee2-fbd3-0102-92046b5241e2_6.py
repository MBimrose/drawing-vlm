from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
wall_thickness = 2.0
groove_width = 20.0
groove_depth = 4.0
hole_diameter = 7.0
hole_count = 6
chamfer_size = 0.8

solid_body = Box(block_length, block_width, block_height)
solid_body = offset(solid_body, amount=-wall_thickness)

groove_box = Box(block_length, groove_width, groove_depth)
solid_body = solid_body - Pos(0, 0, block_height/2 - groove_depth/2) * groove_box
solid_body = solid_body - Pos(0, 0, -block_height/2 + groove_depth/2) * groove_box

hole_spacing = block_length / (hole_count + 1)
for i in range(hole_count):
    x = -block_length/2 + hole_spacing * (i + 1)
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height)

left_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(left_face.edges(), chamfer_size)

part = solid_body
part.name = "shelled_block_with_grooves_and_holes"
export_step(part, "output.step")