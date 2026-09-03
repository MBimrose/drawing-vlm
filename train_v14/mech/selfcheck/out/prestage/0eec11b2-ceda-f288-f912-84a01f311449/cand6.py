from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
channel_radius = 10.0
channel_center_z = block_height / 2.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

with BuildSketch(Plane.XZ) as profile_sk:
    with BuildLine() as pl:
        Line((-channel_radius, 0), (channel_radius, 0))
        ThreePointArc((channel_radius, 0), (0, channel_radius), (-channel_radius, 0))
    make_face()

with BuildLine() as path_bl:
    Line((0, 0, channel_center_z), (block_length, 0, channel_center_z))

channel = sweep(sections=profile_sk.sketch, path=path_bl.line)
result = base - channel

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)

part = result
part.name = "block_with_channel"
export_step(part, "output.step")