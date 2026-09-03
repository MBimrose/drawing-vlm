from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
channel_radius = 12.0
channel_offset = 10.0
boss_diameter = 15.0
boss_height = 10.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
chamfer_size = 1.0

result = Box(block_length, block_width, block_height)

boss = Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

pocket = Pos(0, 0, block_height/2 + boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x, y in [(-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
             (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
             (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
             (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)]:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height + boss_height + 10)
    result = result - hole

with BuildPart() as ch:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((channel_radius, 0), (channel_radius, block_height))
            l2 = Line(l1@1, (channel_radius + wall_thickness, block_height))
            l3 = Line(l2@1, (channel_radius + wall_thickness, 0))
            l4 = Line(l3@1, (channel_radius, 0))
        make_face()
    revolve(axis=Axis.X, revolution_arc=180)

channel_solid = Pos(0, channel_offset, 0) * ch.part
result = result - channel_solid

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_channel"
export_step(part, "output.step")