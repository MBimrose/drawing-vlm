from build123d import *
import math

outer_diameter = 60.0
outer_radius = outer_diameter / 2.0
total_length = 60.0
reduced_diameter = 20.0
reduced_radius = reduced_diameter / 2.0
reduced_section_length = 30.0
end_section_length = (total_length - reduced_section_length) / 2.0
hole_diameter = 6.0
hole_count = 6
hole_radius = outer_radius - 8.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (outer_radius, 0), (outer_radius, end_section_length),
                     (reduced_radius, end_section_length),
                     (reduced_radius, end_section_length + reduced_section_length),
                     (outer_radius, end_section_length + reduced_section_length),
                     (outer_radius, total_length), (0, total_length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_length / 2) * Cylinder(hole_diameter / 2, total_length)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "stepped_shaft_with_holes"
export_step(part, "output.step")