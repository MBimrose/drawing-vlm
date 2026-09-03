from build123d import *
import math

block_length = 100.0
block_width = 60.0
block_height = 80.0
coil_radius = 20.0
coil_pitch = 10.0
coil_height = 60.0
coil_wire_radius = 4.0
pocket_width = 30.0
pocket_height = 15.0
pocket_depth = 50.0
pocket_chamfer = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
post_radius = 4.0
post_height = coil_height + 20.0

base = Box(block_length, block_width, block_height)

helix_pts = []
for i in range(200):
    t = i / 199
    z = t * coil_height
    angle = t * (coil_height / coil_pitch) * 2 * math.pi
    x = coil_radius * math.cos(angle)
    y = coil_radius * math.sin(angle)
    helix_pts.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_path = bl.line

with BuildSketch() as cs:
    Circle(coil_wire_radius)
coil_face = cs.sketch

coil = sweep(sections=coil_face, path=helix_path)
post = Pos(0, 0, post_height / 2) * Cylinder(post_radius, post_height)
result = base + coil + post

pocket = Pos(block_length / 2 - pocket_depth / 2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

pocket_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-4:]
result = chamfer(pocket_edges, pocket_chamfer)

hole_positions = [
    (-block_length / 2 + mount_hole_offset, -block_width / 2 + mount_hole_offset),
    (block_length / 2 - mount_hole_offset, -block_width / 2 + mount_hole_offset),
    (-block_length / 2 + mount_hole_offset, block_width / 2 - mount_hole_offset),
    (block_length / 2 - mount_hole_offset, block_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, block_height + 10)

part = result
part.name = "block_with_coil_pocket_and_mount_holes"
export_step(part, "output.step")