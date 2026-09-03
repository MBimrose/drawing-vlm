from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
channel_radius = 12.0
channel_wall_thickness = 2.0
channel_angle = 120.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
boss_radius = 6.0
boss_height = 10.0
boss_offset_x = 20.0

start_angle = -channel_angle / 2.0
end_angle = channel_angle / 2.0
start_pt = (channel_radius * math.cos(math.radians(start_angle)), channel_radius * math.sin(math.radians(start_angle)))
end_pt = (channel_radius * math.cos(math.radians(end_angle)), channel_radius * math.sin(math.radians(end_angle)))
mid_pt = (channel_radius, 0.0)

base = Box(block_length, block_width, block_height)

with BuildLine() as bl:
    ThreePointArc(start_pt, mid_pt, end_pt)
path_wire = bl.wire()

with BuildSketch() as sk:
    Circle(channel_radius + channel_wall_thickness)
outer_face = sk.face()

with BuildSketch() as sk2:
    Circle(channel_radius)
inner_face = sk2.face()

outer_solid = sweep(sections=outer_face, path=path_wire)
inner_solid = sweep(sections=inner_face, path=path_wire)
channel = outer_solid - inner_solid

result = base - channel

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height * 2)

boss = Pos(boss_offset_x, 0, block_height/2 - boss_height/2) * Cylinder(boss_radius, boss_height)
result = result + boss

part = result
part.name = "block_with_channel"
export_step(part, "output.step")