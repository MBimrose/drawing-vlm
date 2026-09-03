from build123d import *

block_length = 50.0
block_width = 35.0
block_height = 12.0
channel_width = 8.0
channel_depth = block_height - 2.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_offset = 10.0
pocket_radius = 6.0
pocket_depth = 4.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

ch1 = Pos(0, -block_width/2 + channel_width/2, block_height - channel_depth/2) * Box(block_length, channel_width, channel_depth)
ch2 = Pos(-block_length/2 + channel_width/2, 0, block_height - channel_depth/2) * Box(channel_width, block_width, channel_depth)

result = base - ch1 - ch2

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

for x, y in [(hole_offset, hole_offset), (block_length - hole_offset, hole_offset),
             (hole_offset, block_width - hole_offset), (block_length - hole_offset, block_width - hole_offset)]:
    result = result - Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height)

result = result - Pos(block_length/2, block_width/2, block_height - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)

part = result
part.name = "channel_block"
export_step(part, "output.step")