from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
wall_thickness = 3.0
channel_width = 8.0
channel_depth = 12.0
channel_spacing = 12.0
num_channels = 3
chamfer_size = 1.2
fillet_radius = 0.8
hole_diameter = 4.0
hole_depth = 8.0
hole_spacing = 20.0

result = Box(block_length, block_width, block_height)

channel_positions = [
    -block_length/2 + wall_thickness + channel_spacing + i*(channel_width + channel_spacing) + channel_width/2
    for i in range(num_channels)
]

for x in channel_positions:
    channel = Pos(x, 0, block_height/2 - channel_depth/2) * Box(channel_width, block_width, channel_depth)
    result = result - channel

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (-hole_spacing/2, -hole_spacing/2),
    (hole_spacing/2, -hole_spacing/2),
    (-hole_spacing/2, hole_spacing/2),
    (hole_spacing/2, hole_spacing/2)
]

for hx, hy in hole_positions:
    hole = Pos(hx, hy, -block_height/2 + hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    result = result - hole

part = result
part.name = "channel_block"
export_step(part, "output.step")