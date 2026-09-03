from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
channel_radius = 10.0
channel_wall_thickness = 2.0
channel_angle = 120.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0

base = Box(block_length, block_width, block_height)

with BuildSketch(Plane.XZ) as profile_sk:
    Circle(channel_radius)

with BuildLine() as path_bl:
    RadiusArc((0, 0), (channel_radius * 2, 0), channel_radius)

with BuildPart() as channel_bp:
    sweep(sections=profile_sk.sketch, path=path_bl.line)

channel_solid = channel_bp.part
channel_solid = offset(channel_solid, amount=-channel_wall_thickness)

result = base - channel_solid

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

px = block_length / 2 - mount_hole_offset
py = block_width / 2 - mount_hole_offset
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, block_height * 2)

part = result
part.name = "block_with_channel"
export_step(part, "output.step")