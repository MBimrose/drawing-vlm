from build123d import *
import math

shaft_radius = 8.0
shaft_length = 60.0
flange_radius = 38.0
flange_thickness = 20.0
rib_height = 4.0
rib_width = 6.0
hole_diameter = 5.0
hole_depth = 10.0
hole_offset_radius = 20.0
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

rib = Pos(0, 0, shaft_length + flange_thickness / 2) * (Cylinder(flange_radius, rib_height) - Cylinder(flange_radius - rib_width, rib_height))
solid_body = solid_body + rib

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_offset_radius * math.cos(angle)
    py = hole_offset_radius * math.sin(angle)
    hole = Pos(px, py, shaft_length + flange_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "shaft_with_flange_and_ribs"
export_step(part, "output.step")