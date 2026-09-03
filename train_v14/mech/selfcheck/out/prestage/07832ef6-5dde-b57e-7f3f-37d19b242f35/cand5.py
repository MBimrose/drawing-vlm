from build123d import *
import math

shaft_radius = 8.0
shaft_length = 60.0
flange_outer_radius = 38.0
flange_thickness = 20.0
hole_diameter = 5.0
hole_depth = 10.0
hole_pattern_radius = 20.0
hole_count = 4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1 @ 1, (shaft_radius, shaft_length))
            l3 = Line(l2 @ 1, (flange_outer_radius, shaft_length))
            l4 = Line(l3 @ 1, (flange_outer_radius, shaft_length + flange_thickness))
            l5 = Line(l4 @ 1, (0, shaft_length + flange_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_z = shaft_length + flange_thickness

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, top_z - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "shaft_with_flange_and_holes"
export_step(part, "output.step")