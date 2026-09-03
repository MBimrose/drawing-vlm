from build123d import *
import math

block_length = 100.0
block_width = 60.0
block_height = 80.0
groove_width = 5.0
groove_depth = 3.0
groove_pitch = 10.0
groove_turns = 5
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
boss_diameter = 8.0
boss_height = 10.0
slot_width = 15.0
slot_depth = 5.0

with BuildPart() as p:
    Box(block_length, block_width, block_height)

solid_body = p.part

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height * 2)

solid_body = solid_body + Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

slot_box = Pos(block_length/2 - slot_depth/2, 0, 0) * Box(block_length, slot_depth, slot_width)
solid_body = solid_body - slot_box

helix_radius = (block_width/2) - groove_depth - 2.0
helix_pts = []
for i in range(200):
    t = i / 199
    angle = 2 * math.pi * groove_turns * t
    z = -block_height/2 + t * block_height
    helix_pts.append(Vector(helix_radius * math.cos(angle), helix_radius * math.sin(angle), z))

with BuildLine() as bl:
    Polyline(*helix_pts)
helix_path = bl.line

with BuildSketch() as sk:
    Rectangle(groove_width, groove_depth)
profile_face = Pos(helix_radius, 0, -block_height/2) * sk.sketch

groove = sweep(sections=profile_face, path=helix_path)
solid_body = solid_body - groove

part = solid_body
part.name = "helical_groove_block"
export_step(part, "output.step")