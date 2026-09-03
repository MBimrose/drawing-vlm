from build123d import *
import math

total_length = 80.0
small_diameter = 30.0
large_diameter = 60.0
wall_thickness = 3.0
rib_height = 5.0
rib_width = 10.0
rib_position = 20.0
thread_diameter = 10.0
thread_pitch = 2.0
thread_length = 30.0
chamfer_size = 1.0

small_radius = small_diameter / 2.0
large_radius = large_diameter / 2.0
inner_small_radius = small_radius - wall_thickness
inner_large_radius = large_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (small_radius, 0))
            l2 = Line(l1 @ 1, (small_radius, total_length * 0.2))
            l3 = Line(l2 @ 1, (large_radius, total_length))
            l4 = Line(l3 @ 1, (0, total_length))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, rib_position) * Cylinder(inner_small_radius + rib_height, rib_width)
solid_body = solid_body + rib

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

thread_cutter = Pos(0, 0, thread_length / 2) * Cylinder(thread_diameter / 2.0, thread_length)
solid_body = solid_body - thread_cutter

part = solid_body
part.name = "hollow_cone_with_rib"
export_step(part, "output.step")