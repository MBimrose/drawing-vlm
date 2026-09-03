from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
wall_thickness = 2.0
chamfer_distance = 0.8
hole_diameter = 5.0
hole_count = 7
hole_spacing = (block_length - 2 * wall_thickness) / (hole_count - 1)
pocket_length = 80.0
pocket_width = 30.0
pocket_depth = 10.0

solid_body = Box(block_length, block_width, block_height)
solid_body = offset(solid_body, amount=-wall_thickness)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_count):
    x = -block_length/2 + wall_thickness + i * hole_spacing
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height)
    solid_body = solid_body - hole

x_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(x_face.edges(), chamfer_distance)

part = solid_body
part.name = "shelled_block_with_pocket_and_holes"
export_step(part, "output.step")