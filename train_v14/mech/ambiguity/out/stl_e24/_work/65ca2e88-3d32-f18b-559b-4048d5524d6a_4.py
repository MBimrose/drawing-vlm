from build123d import *
import math

block_length = 100.0
block_width = 60.0
block_height = 80.0
thread_pitch = 10.0
thread_depth = 5.0
thread_major_dia = 40.0
thread_minor_dia = thread_major_dia - 2 * thread_depth
thread_turns = 5
thread_height = thread_pitch * thread_turns
slot_width = 10.0
slot_depth = 15.0
slot_offset = 5.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
boss_radius = 4.0
boss_height = block_height + thread_height

base = Box(block_length, block_width, block_height)
boss = Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

with BuildPart() as tp:
    with BuildSketch() as ts:
        with BuildLine() as tl:
            Polyline((thread_minor_dia/2, 0), (thread_major_dia/2, 0), (thread_major_dia/2, thread_pitch/2), close=True)
        make_face()
    extrude(amount=thread_height, taper=360*thread_turns)
thread_solid = Pos(0, 0, -thread_height/2) * tp.part
result = result - thread_solid

slot = Pos(0, slot_offset, 0) * Box(block_length, slot_width, slot_depth)
result = result - slot

hole_positions = [
    (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height + 10)

part = result
part.name = "threaded_block_with_slot"
export_step(part, "output.step")