from build123d import *
import math

block_length = 100.0
block_width = 60.0
block_height = 80.0
groove_radius = 20.0
groove_width = 5.0
groove_pitch = 10.0
groove_turns = 3
groove_height = groove_pitch * groove_turns
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
slot_width = 15.0
slot_height = 10.0
slot_depth = block_width - 2 * mount_hole_offset
boss_radius = 4.0
boss_height = 10.0

solid_body = Box(block_length, block_width, block_height)

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height)

solid_body = solid_body - Pos(block_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)

solid_body = solid_body + Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

helix_radius = groove_radius + groove_width/2
num_points = 200
helix_points = []
for i in range(num_points):
    t = i / (num_points - 1)
    angle = 2 * math.pi * groove_turns * t
    z = t * groove_height
    x = helix_radius * math.cos(angle)
    y = helix_radius * math.sin(angle)
    helix_points.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_points)
helix_path = bl.wire()

with BuildSketch() as sk:
    Circle(groove_width/2)
groove_profile = sk.face()

groove_solid = sweep(sections=groove_profile, path=helix_path)
solid_body = solid_body - groove_solid

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "grooved_block"
export_step(part, "output.step")