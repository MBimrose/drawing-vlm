from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
block_height = 40.0
shoulder_height = 10.0
central_hole_radius = 8.0
tap_hole_radius = 2.5
tap_hole_count = 6
tap_hole_circle_radius = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, block_height - shoulder_height))
            l3 = Line(l2 @ 1, (inner_radius, block_height - shoulder_height))
            l4 = Line(l3 @ 1, (inner_radius, block_height))
            l5 = Line(l4 @ 1, (0, block_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, block_height / 2) * Cylinder(central_hole_radius, block_height)

for i in range(tap_hole_count):
    angle = math.radians(i * 360.0 / tap_hole_count)
    px = tap_hole_circle_radius * math.cos(angle)
    py = tap_hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, block_height / 2) * Cylinder(tap_hole_radius, block_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_block_with_holes"
export_step(part, "output.step")