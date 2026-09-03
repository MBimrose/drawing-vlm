from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
channel_radius = 8.0
channel_angle = 120.0
channel_length = 40.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0

start_pt = (0, 0, 0)
end_pt = (channel_length * math.cos(math.radians(channel_angle)), 0, channel_length * math.sin(math.radians(channel_angle)))
mid_pt = (channel_length * 0.5, 0, channel_length * 0.5)

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(channel_radius)
    with BuildLine() as bl:
        ThreePointArc(Vector(start_pt), Vector(mid_pt), Vector(end_pt))
    sweep(sections=s.sketch, path=bl.line)
channel = p.part

result = base - channel

px = block_length/2 - mount_hole_offset
py = block_width/2 - mount_hole_offset
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    result = result - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)

part = result
part.name = "block_with_channel_and_mount_holes"
export_step(part, "output.step")