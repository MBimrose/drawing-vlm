from build123d import *

block_width = 50.0
block_depth = 35.0
block_height = 12.0
channel_width = 8.0
channel_depth = 8.0
pocket_diameter = 10.0
pocket_depth = 12.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_offset = 10.0

base = Pos(-block_width/2, -block_depth/2, block_height/2) * Box(block_width, block_depth, block_height)

ch1 = Pos(-block_width/2 + channel_width/2, -block_depth/2 + channel_depth/2, block_height/2) * Box(channel_width, block_depth - channel_depth, channel_depth)
ch2 = Pos(-block_width/2 + channel_depth/2, -block_depth/2 + channel_width/2, block_height/2) * Box(block_width - channel_depth, channel_width, channel_depth)
channel = ch1 + ch2

pocket = Pos(0, 0, block_height/2) * Cylinder(pocket_diameter/2, pocket_depth)

result = base - channel - pocket

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

result = result - Pos(hole_offset, hole_offset, block_height/2) * Cylinder(hole_diameter/2, block_height + 1)

part = result
part.name = "channel_block"
export_step(part, "output.step")