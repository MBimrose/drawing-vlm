from build123d import *
import math

block_length = 100.0
block_width = 60.0
block_height = 80.0
spring_outer_radius = 20.0
spring_inner_radius = 15.0
spring_pitch = 10.0
spring_turns = 5
spring_height = spring_pitch * spring_turns
spring_wire_radius = 2.0
pocket_width = 30.0
pocket_height = 15.0
pocket_depth = 5.0
pocket_chamfer = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
central_spine_radius = 4.0

base = Box(block_length, block_width, block_height)

num_points = 200
helix_points = []
for i in range(num_points):
    t = i / (num_points - 1)
    angle = 2 * math.pi * spring_turns * t
    radius = spring_inner_radius + (spring_outer_radius - spring_inner_radius) * (0.5 + 0.5 * math.sin(angle))
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = spring_height * t - spring_height / 2
    helix_points.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_points)
helix_path = bl.line

with BuildSketch() as bs:
    Circle(spring_wire_radius)
wire_profile = bs.sketch

spring = sweep(sections=wire_profile, path=helix_path)

result = base + spring

pocket = Pos(block_length/2 - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

pocket_edges = [e for e in result.edges().filter_by(Axis.Z) if abs(e.center().X - block_length/2) < 0.5]
result = chamfer(pocket_edges, pocket_chamfer)

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
    (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

spine = Pos(0, 0, block_height/2) * Cylinder(central_spine_radius, block_height)
result = result + spine

part = result
part.name = "spring_block"
export_step(part, "output.step")