from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
channel_width = 10.0
channel_depth = 10.0
fillet_radius = 1.0
hole_diameter = 5.0
hole_offset = 10.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
channel1 = Pos(0, 0, block_height - channel_depth/2) * Box(channel_width, block_width, channel_depth)
channel2 = Pos(0, 0, block_height - channel_depth/2) * Box(block_length, channel_width, channel_depth)

result = base - channel1 - channel2

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)
bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

hole1 = Pos(0, -block_width/2 + hole_offset, block_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, block_length)
hole2 = Pos(0, block_width/2 - hole_offset, block_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, block_length)
result = result - hole1 - hole2

part = result
part.name = "channel_block"
export_step(part, "output.step")