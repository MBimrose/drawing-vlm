from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
channel_width = 12.0
channel_depth = 8.0
channel_arc_radius = 30.0
channel_arc_angle = 120.0
rib_thickness = 4.0
rib_height = 6.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
chamfer_size = 1.0

arc_start_angle = -channel_arc_angle / 2.0
arc_end_angle = channel_arc_angle / 2.0
arc_start = (math.cos(math.radians(arc_start_angle)) * channel_arc_radius,
             math.sin(math.radians(arc_start_angle)) * channel_arc_radius)
arc_end = (math.cos(math.radians(arc_end_angle)) * channel_arc_radius,
           math.sin(math.radians(arc_end_angle)) * channel_arc_radius)
arc_mid = (channel_arc_radius, 0.0)

base = Pos(0, 0, block_height / 2) * Box(block_length, block_width, block_height)

with BuildLine() as bl:
    ThreePointArc(arc_start, arc_mid, arc_end)
path = bl.wire()

with BuildSketch() as sk:
    Rectangle(channel_width, channel_depth)
profile = sk.face()

channel = sweep(sections=profile, path=path)
result = base - channel

rib = Pos(0, 0, block_height - rib_height / 2) * Box(rib_thickness, block_width - 2 * mount_hole_offset, rib_height)
result = result + rib

hole_positions = [
    (-block_length / 2 + mount_hole_offset, -block_width / 2 + mount_hole_offset),
    (block_length / 2 - mount_hole_offset, -block_width / 2 + mount_hole_offset),
    (-block_length / 2 + mount_hole_offset, block_width / 2 - mount_hole_offset),
    (block_length / 2 - mount_hole_offset, block_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, block_height / 2) * Cylinder(mount_hole_dia / 2, block_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_channel"
export_step(part, "output.step")