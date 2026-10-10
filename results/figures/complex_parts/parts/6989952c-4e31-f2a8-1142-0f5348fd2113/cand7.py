from build123d import *
import math

outer_radius = 30.0
flange_thickness = 15.0
web_radius = 10.0
web_length = 30.0
hole_diameter = 6.0
hole_count = 6
hole_circle_radius = 22.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(
                (0, -(web_length/2 + flange_thickness)),
                (outer_radius, -(web_length/2 + flange_thickness)),
                (outer_radius, -web_length/2),
                (web_radius, -web_length/2),
                (web_radius, web_length/2),
                (outer_radius, web_length/2),
                (outer_radius, web_length/2 + flange_thickness),
                (0, web_length/2 + flange_thickness),
                close=True
            )
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, 100)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "revolved_flange_with_holes"
export_step(part, "output.step")