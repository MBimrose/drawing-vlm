from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
channel_radius = 12.0
channel_angle = 120.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 3.0

base = Box(block_length, block_width, block_height)
rib = Pos(0, block_width/2 - rib_width/2 - wall_thickness, block_height/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
result = base + rib

with BuildPart() as ch:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_radius, 0))
            a1 = ThreePointArc(l1 @ 1, (channel_radius, channel_radius), (0, channel_radius))
            l2 = Line(a1 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z, revolution_arc=channel_angle)
channel_solid = Pos(0, 0, block_height/2) * ch.part
result = result - channel_solid

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height * 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_channel"
export_step(part, "output.step")