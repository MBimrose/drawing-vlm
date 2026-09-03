from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
wall_thickness = 2.0
channel_width = 30.0
channel_height = 20.0
hole_diameter = 5.0
hole_count = 6
chamfer_distance = 0.8

solid_body = Box(block_length, block_width, block_height)
solid_body = offset(solid_body, amount=-wall_thickness)

channel_cut = Box(channel_width, block_height, channel_height)
solid_body = solid_body - channel_cut

hole_spacing = (block_length - 2 * wall_thickness) / (hole_count - 1)
for i in range(hole_count):
    x = -block_length / 2 + wall_thickness + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, block_height)

x_face = solid_body.faces().sort_by(Axis.X)[0]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_distance)

part = solid_body
part.name = "shelled_block_with_channel_and_holes"
export_step(part, "output.step")