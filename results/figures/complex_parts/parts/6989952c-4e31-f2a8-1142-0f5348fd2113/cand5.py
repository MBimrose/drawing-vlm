from build123d import *
import math

outer_radius = 30.0
inner_radius = 10.0
web_height = 30.0
flange_thickness = 15.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_count = 6
hole_pattern_radius = 22.0

total_height = web_height + 2 * flange_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (outer_radius, 0), (outer_radius, flange_thickness),
                     (inner_radius, flange_thickness), (inner_radius, flange_thickness + web_height),
                     (outer_radius, flange_thickness + web_height), (outer_radius, total_height),
                     (inner_radius, total_height), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 20)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "revolved_flange_with_holes"
export_step(part, "output.step")