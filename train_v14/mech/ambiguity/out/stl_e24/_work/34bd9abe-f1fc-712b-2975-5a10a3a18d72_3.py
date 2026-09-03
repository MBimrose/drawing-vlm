from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
channel_width_top = 12.0
channel_depth_top = 5.0
channel_width_bottom = 6.0
channel_depth_bottom = 10.0
fillet_radius = 1.0
hole_diameter = 5.0
hole_offset = 10.0

solid_body = Box(block_length, block_width, block_height)

solid_body = solid_body - Pos(0, 0, block_height/2 - channel_depth_top/2) * Box(channel_width_top, block_length, channel_depth_top)
solid_body = solid_body - Pos(0, 0, block_height/2 - channel_depth_bottom/2) * Box(channel_width_bottom, block_length, channel_depth_bottom)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = fillet(solid_body.edges().sort_by(Axis.Z)[:4], fillet_radius)

for y in [-block_width/2 + hole_offset, block_width/2 - hole_offset]:
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, block_length)

part = solid_body
part.name = "stepped_channel_block"
export_step(part, "output.step")