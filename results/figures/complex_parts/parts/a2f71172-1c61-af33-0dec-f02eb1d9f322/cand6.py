from build123d import *
import math

outer_radius = 30.0
shoulder_radius = 20.0
total_height = 40.0
shoulder_height = 10.0
bore_radius = 8.0
hole_diameter = 5.0
hole_depth = 30.0
hole_circle_radius = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, total_height - shoulder_height))
            l3 = Line(l2 @ 1, (shoulder_radius, total_height - shoulder_height))
            l4 = Line(l3 @ 1, (shoulder_radius, total_height))
            l5 = Line(l4 @ 1, (0, total_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(bore_radius, total_height)

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "stepped_cylinder_with_holes"
export_step(part, "output.step")