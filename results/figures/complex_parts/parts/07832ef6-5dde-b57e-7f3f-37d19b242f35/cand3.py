from build123d import *
import math

shaft_length = 60.0
shaft_radius = 8.0
flange_thickness = 20.0
flange_radius = 38.0
hole_diameter = 5.0
hole_depth = 10.0
hole_pattern_radius = 20.0
hole_count = 4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (shaft_radius, 0), (shaft_radius, shaft_length),
                     (flange_radius, shaft_length), (flange_radius, shaft_length + flange_thickness),
                     (0, shaft_length + flange_thickness), close=True)
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