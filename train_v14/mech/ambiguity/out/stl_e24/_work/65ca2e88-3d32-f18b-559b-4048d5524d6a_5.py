from build123d import *
import math

body_length = 100.0
body_width = 60.0
body_height = 80.0
shaft_diameter = 8.0
thread_pitch = 10.0
thread_depth = 2.0
thread_length = body_length
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
slot_width = 15.0
slot_height = 30.0
slot_depth = 10.0

result = Box(body_length, body_width, body_height)

slot = Pos(0, 0, body_height/2 - slot_depth/2) * Box(slot_width, slot_height, slot_depth)
result = result - slot

hole_positions = [
    (-body_length/2 + mount_hole_offset, -body_width/2 + mount_hole_offset),
    ( body_length/2 - mount_hole_offset, -body_width/2 + mount_hole_offset),
    ( body_length/2 - mount_hole_offset,  body_width/2 - mount_hole_offset),
    (-body_length/2 + mount_hole_offset,  body_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, body_height)

shaft = Pos(0, 0, body_height/2 + thread_length/2) * Cylinder(shaft_diameter/2, thread_length)
result = result + shaft

num_points = 200
helix_pts = []
for i in range(num_points):
    t = i / (num_points - 1)
    angle = 2 * math.pi * t * (thread_length / thread_pitch)
    r = shaft_diameter/2 + thread_depth/2
    helix_pts.append(Vector(r * math.cos(angle), r * math.sin(angle), t * thread_length))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_path = bl.wire()

with BuildSketch() as sk:
    Circle(thread_depth)
thread_profile = sk.face()

thread_cut = sweep(sections=thread_profile, path=helix_path)
thread_cut = Pos(0, 0, body_height/2) * thread_cut
result = result - thread_cut

part = result
part.name = "threaded_shaft_with_mounting_holes"
export_step(part, "output.step")