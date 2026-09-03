from build123d import *
import math

block_length = 100.0
block_width = 60.0
block_height = 80.0
boss_diameter = 20.0
boss_height = 15.0
thread_pitch = 12.0
thread_turns = 5
thread_radius = 3.0
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(mount_hole_dia/2, block_height + 20)

helix_radius = boss_diameter/2 + thread_radius
num_points = 200
helix_pts = []
for i in range(num_points):
    t = i / (num_points - 1)
    angle = 2 * math.pi * thread_turns * t
    z = block_height * t
    x = helix_radius * math.cos(angle)
    y = helix_radius * math.sin(angle)
    helix_pts.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_wire = bl.wire()

with BuildSketch() as ts:
    Circle(thread_radius)
thread_face = ts.sketch

thread_solid = sweep(sections=thread_face, path=helix_wire)
solid_body = solid_body - thread_solid

part = solid_body
part.name = "threaded_block"
export_step(part, "output.step")