from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 15.0
channel_width = 10.0
channel_depth = 9.0
channel_offset = 5.0
blind_hole_diameter = 6.0
blind_hole_depth = 8.0
blind_hole_offset_y = 10.0
chamfer_size = 1.0
mount_hole_diameter = 2.5
mount_hole_spacing = 25.0
mount_hole_rows = 2
mount_hole_cols = 2

result = Box(block_length, block_width, block_height)

channel_cut = Pos(0, -block_width/2 + channel_offset, 0) * Box(block_length, channel_width, channel_depth)
result = result - channel_cut

blind_hole = Pos(block_length/2 - blind_hole_depth/2, -block_width/2 + blind_hole_offset_y, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - blind_hole

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols - 1) / 2) * mount_hole_spacing
        y = (j - (mount_hole_rows - 1) / 2) * mount_hole_spacing
        result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 1)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "block_with_channel_and_holes"
export_step(part, "output.step")